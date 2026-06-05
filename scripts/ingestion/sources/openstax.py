"""
OpenStax Scraper
================
Fetches all Grade 6–12 textbooks from OpenStax via their public API
(openstax.org/api/v2/books).

Content structure:  Book → Unit → Chapter → Section → Page (CNXML/HTML)

License: CC BY 4.0 — all content freely redistributable with attribution.
"""
from __future__ import annotations

import logging
import re
from typing import Any, AsyncIterator

from bs4 import BeautifulSoup

from scripts.ingestion.config import SOURCES, SUBJECT_NORMALISATION
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

_API_BASE   = "https://openstax.org/api/v2"
_BOOKS_URL  = f"{_API_BASE}/books"

# Map OpenStax book slugs to grade range + CAPS subject
_BOOK_CAPS_MAP: dict[str, dict[str, Any]] = {
    # Mathematics
    "prealgebra-2e":        {"subject": "mathematics", "grades": [7, 8, 9]},
    "elementary-algebra-2e":{"subject": "mathematics", "grades": [8, 9, 10]},
    "intermediate-algebra-2e":{"subject": "mathematics","grades": [10, 11]},
    "algebra-and-trigonometry-2e":{"subject":"mathematics","grades":[11, 12]},
    "precalculus-2e":       {"subject": "mathematics", "grades": [11, 12]},
    "calculus-volume-1":    {"subject": "mathematics", "grades": [12]},
    "calculus-volume-2":    {"subject": "mathematics", "grades": [12]},
    "statistics":           {"subject": "mathematics", "grades": [10, 11, 12]},
    # Sciences
    "biology-2e":           {"subject": "life_sciences",     "grades": [10, 11, 12]},
    "microbiology":         {"subject": "life_sciences",     "grades": [11, 12]},
    "anatomy-and-physiology":{"subject":"life_sciences",     "grades": [11, 12]},
    "chemistry-2e":         {"subject": "physical_sciences", "grades": [10, 11, 12]},
    "chemistry-atoms-first-2e":{"subject":"physical_sciences","grades":[10,11,12]},
    "university-physics-volume-1":{"subject":"physical_sciences","grades":[11,12]},
    "university-physics-volume-2":{"subject":"physical_sciences","grades":[12]},
    "college-physics-2e":   {"subject": "physical_sciences", "grades": [10, 11, 12]},
    "astronomy-2e":         {"subject": "natural_sciences",  "grades": [10, 11]},
    "earth-science":        {"subject": "natural_sciences",  "grades": [9, 10]},
    # Humanities
    "us-history":           {"subject": "history",    "grades": [9, 10, 11]},
    "world-history-volume-1":{"subject":"history",    "grades": [9, 10]},
    "world-history-volume-2":{"subject":"history",    "grades": [10, 11]},
    "principles-economics-3e":{"subject":"economics", "grades": [11, 12]},
    "principles-microeconomics-3e":{"subject":"economics","grades":[11,12]},
    "principles-macroeconomics-3e":{"subject":"economics","grades":[11,12]},
    # English
    "writing-guide-with-handbook":{"subject":"english_home_language","grades":[10,11,12]},
}


class OpenStaxScraper(BaseScraper):
    """
    Ingests OpenStax textbook content section by section.
    Each section becomes one RawContent record.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["openstax"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        books = await self._get(_BOOKS_URL)
        if not isinstance(books, dict):
            logger.error("[OpenStax] Failed to fetch book list")
            return

        book_list = books.get("books", [])
        self._total = len(book_list)
        logger.info("[OpenStax] Found %d books", self._total)

        for i, book_meta in enumerate(book_list):
            if self._at_limit():
                break
            slug = book_meta.get("meta", {}).get("slug") or book_meta.get("slug", "")
            caps_info = _BOOK_CAPS_MAP.get(slug)
            if not caps_info:
                logger.debug("[OpenStax] Skipping unmapped book: %s", slug)
                continue

            grade_lo, grade_hi = self.grade_range
            book_grades = caps_info["grades"]
            if not any(grade_lo <= g <= grade_hi for g in book_grades):
                continue

            self._emit(i, self._total, f"Book: {slug}")
            async for item in self._scrape_book(book_meta, caps_info):
                if self._at_limit():
                    return
                yield item

    async def _scrape_book(
        self, meta: dict[str, Any], caps_info: dict[str, Any]
    ) -> AsyncIterator[RawContent]:
        book_id   = meta.get("id") or meta.get("meta", {}).get("id")
        book_slug = meta.get("meta", {}).get("slug") or meta.get("slug", book_id)
        book_url  = f"{_API_BASE}/books/{book_id}"
        book_data = await self._get(book_url)
        if not isinstance(book_data, dict):
            return

        title = book_data.get("title", book_slug)
        tree  = book_data.get("table_of_contents", {})
        logger.info("[OpenStax] Book: %s — walking ToC", title)

        async for item in self._walk_toc(tree, book_slug, title, caps_info):
            yield item

    async def _walk_toc(
        self, node: dict[str, Any], book_slug: str, book_title: str,
        caps_info: dict[str, Any], chapter: str = ""
    ) -> AsyncIterator[RawContent]:
        contents = node.get("contents", [])
        for child in contents:
            slug  = child.get("slug", "")
            kind  = child.get("id", "")
            title = child.get("title", slug)

            # Unit / Chapter node — recurse
            if child.get("contents"):
                chapter_label = title if not chapter else chapter
                async for item in self._walk_toc(child, book_slug, book_title,
                                                  caps_info, chapter_label):
                    yield item
                continue

            # Page leaf node
            page_url = f"https://openstax.org/books/{book_slug}/pages/{slug}"
            item = await self._fetch_page(page_url, slug, title, book_title,
                                           chapter, caps_info)
            if item:
                self._done += 1
                yield item

    async def _fetch_page(
        self, url: str, slug: str, title: str, book_title: str,
        chapter: str, caps_info: dict[str, Any]
    ) -> RawContent | None:
        # OpenStax pages are rendered as full HTML
        html = await self._get(f"{_API_BASE}/pages/{slug}")
        if not html:
            # Fall back: fetch the rendered page
            html = await self._get(url)
        if not html:
            return None

        if isinstance(html, dict):
            html = html.get("content") or html.get("html_body") or ""

        soup  = BeautifulSoup(str(html), "html.parser")
        # Remove nav, sidebar, ToC elements
        for tag in soup.select("nav, .toc, .sidebar, script, style"):
            tag.decompose()

        plain = soup.get_text(separator="\n", strip=True)
        # Trim boilerplate
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()

        if len(plain) < 100:
            return None

        return RawContent(
            source_id          = "openstax",
            source_url         = url,
            source_internal_id = slug,
            raw_text           = plain,
            raw_html           = str(html),
            metadata           = {
                "kind":      "textbook_section",
                "book":      book_title,
                "chapter":   chapter,
                "title":     title,
                "subject":   caps_info["subject"],
                "grades":    caps_info["grades"],
            },
            license  = "CC BY 4.0",
            language = "en",
        )
