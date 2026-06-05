"""
Khan Academy Scraper
====================
Walks the public KA topic-tree API (/api/v1/topictree) and collects
Exercises (MCQ + hints) and Articles (lesson text) for Grades 1–12.

KA Content kinds:  Topic | Exercise | Article | Video
We collect: Exercise (items + hints) and Article (body text).
Videos are skipped — we don't want to redistribute video binaries,
but transcript text can be added later via the /video endpoint.

Rate limit: 0.5 RPS (generous — KA is public and open licensed).
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

from bs4 import BeautifulSoup

from scripts.ingestion.config import SOURCES, KA_TOPIC_TO_CAPS
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

_KA_BASE    = "https://www.khanacademy.org"
_API_BASE   = f"{_KA_BASE}/api/v1"
_TREE_URL   = f"{_API_BASE}/topictree"

# KA slugs that map to Grade 1–12 content (skip college/test-prep)
_GRADE_DOMAINS = {
    "math", "science", "computing", "humanities",
    "ela", "economics-finance-domain", "health-and-medicine",
}


class KhanAcademyScraper(BaseScraper):
    """
    Scrapes Khan Academy via its public REST API.

    Traverses: topictree → domain → subject → tutorial → exercise/article
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["khan_academy"], **kwargs)

    # ── Public interface ──────────────────────────────────────────────────────

    async def scrape(self) -> AsyncIterator[RawContent]:
        logger.info("[KhanAcademy] Fetching topic tree …")
        tree = await self._get(_TREE_URL)
        if not tree or not isinstance(tree, dict):
            logger.error("[KhanAcademy] Failed to fetch topic tree")
            return

        children = tree.get("children", [])
        self._total = len(children)
        logger.info("[KhanAcademy] Found %d top-level domains", self._total)

        for i, domain in enumerate(children):
            if self._at_limit():
                break
            slug = domain.get("slug", "")
            if slug not in _GRADE_DOMAINS:
                continue
            self._emit(i, self._total, f"Domain: {slug}")
            async for item in self._walk_node(domain, depth=0):
                if self._at_limit():
                    return
                yield item

    # ── Tree walker ───────────────────────────────────────────────────────────

    async def _walk_node(self, node: dict[str, Any], depth: int) -> AsyncIterator[RawContent]:
        """Recursively walk the topic tree, yielding content at leaf nodes."""
        kind = node.get("kind", "")

        if kind == "Exercise":
            item = await self._fetch_exercise(node)
            if item:
                self._done += 1
                yield item
            return

        if kind == "Article":
            item = await self._fetch_article(node)
            if item:
                self._done += 1
                yield item
            return

        # Topic / Subject / Tutorial — recurse into children
        if kind in {"Topic", "Subject", "Domain", "Tutorial", "Course"}:
            for child in node.get("children", []):
                if self._at_limit():
                    return
                async for item in self._walk_node(child, depth + 1):
                    yield item
            return

        # If we only have a node_url and no children, fetch the full node
        if not node.get("children") and node.get("node_url"):
            full = await self._get(f"{_API_BASE}/topic{node['node_url']}")
            if full and isinstance(full, dict):
                async for item in self._walk_node(full, depth):
                    yield item

    # ── Exercise fetcher ──────────────────────────────────────────────────────

    async def _fetch_exercise(self, node: dict[str, Any]) -> RawContent | None:
        slug = node.get("slug") or node.get("id", "")
        url  = f"{_API_BASE}/exercises/{slug}"
        data = await self._get(url)
        if not data or not isinstance(data, dict):
            # Fall back to node data itself
            data = node

        # Collect assessment items (MCQs)
        items_url = f"{_API_BASE}/exercises/{slug}/assessment_items"
        items_data = await self._get(items_url)

        questions: list[dict[str, Any]] = []
        if isinstance(items_data, list):
            for ai in items_data[:20]:    # cap per-exercise item count
                q = self._parse_assessment_item(ai)
                if q:
                    questions.append(q)

        display_name = data.get("display_name") or data.get("title") or slug
        description  = data.get("short_description") or data.get("description") or ""
        topic_slug   = self._infer_topic_slug(data)
        caps_meta    = KA_TOPIC_TO_CAPS.get(topic_slug, {})

        return RawContent(
            source_id          = "khan_academy",
            source_url         = f"{_KA_BASE}/e/{slug}",
            source_internal_id = slug,
            raw_text           = description,
            raw_json           = {"questions": questions, "node": data, "caps_meta": caps_meta},
            metadata           = {
                "kind":         "exercise",
                "title":        display_name,
                "topic_slug":   topic_slug,
                "ka_grade":     data.get("grade_override"),
                "subject":      data.get("subject_slug"),
                "caps_grades":  caps_meta.get("grades"),
                "caps_topic":   caps_meta.get("topic_code"),
                "ka_subject":   data.get("subject_page_url", ""),
            },
            license = "CC BY-NC-SA 4.0",
            language = "en",
        )

    # ── Article fetcher ───────────────────────────────────────────────────────

    async def _fetch_article(self, node: dict[str, Any]) -> RawContent | None:
        slug = node.get("slug") or node.get("id", "")
        url  = f"{_API_BASE}/articles/{slug}"
        data = await self._get(url)
        if not data or not isinstance(data, dict):
            data = node

        html  = data.get("download_urls", {}).get("html") or data.get("html_body", "")
        if not html:
            return None

        soup      = BeautifulSoup(html, "html.parser")
        plain     = soup.get_text(separator="\n", strip=True)
        title     = data.get("title") or node.get("title", slug)
        topic_slug = self._infer_topic_slug(data)
        caps_meta  = KA_TOPIC_TO_CAPS.get(topic_slug, {})

        return RawContent(
            source_id          = "khan_academy",
            source_url         = f"{_KA_BASE}/a/{slug}",
            source_internal_id = slug,
            raw_text           = plain,
            raw_html           = html,
            raw_json           = {"node": data, "caps_meta": caps_meta},
            metadata           = {
                "kind":       "article",
                "title":      title,
                "topic_slug": topic_slug,
                "caps_grades": caps_meta.get("grades"),
                "caps_topic":  caps_meta.get("topic_code"),
            },
            license  = "CC BY-NC-SA 4.0",
            language = "en",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_assessment_item(ai: dict[str, Any]) -> dict[str, Any] | None:
        """Extract question, options, answer, and hint from a KA assessment item."""
        try:
            item_data = ai.get("item_data") or ai
            if isinstance(item_data, str):
                item_data = json.loads(item_data)

            question = item_data.get("question", {})
            q_text   = BeautifulSoup(question.get("content", ""), "html.parser").get_text(strip=True)

            answers  = item_data.get("answers", [])
            options  = [
                BeautifulSoup(a.get("content", ""), "html.parser").get_text(strip=True)
                for a in answers
            ]
            correct_indices = [i for i, a in enumerate(answers) if a.get("correct")]
            correct = options[correct_indices[0]] if correct_indices and options else None

            hints   = [
                BeautifulSoup(h.get("content", ""), "html.parser").get_text(strip=True)
                for h in item_data.get("hints", [])
            ]

            if not q_text:
                return None
            return {
                "question":    q_text,
                "options":     options,
                "answer":      correct,
                "explanation": "\n".join(hints),
            }
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _infer_topic_slug(data: dict[str, Any]) -> str:
        """Best-effort extraction of the KA topic slug from node metadata."""
        for key in ("topic_slug", "subject_slug", "exercise_model", "slug"):
            val = data.get(key)
            if val:
                return str(val)
        # Try to infer from node URL like "/math/algebra"
        node_url = data.get("node_url", "")
        parts    = [p for p in node_url.split("/") if p]
        return parts[1] if len(parts) >= 2 else ""
