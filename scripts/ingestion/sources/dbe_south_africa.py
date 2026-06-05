"""
DBE South Africa Scraper
=========================
Downloads publicly available materials from the Department of Basic Education:

  1. Mind the Gap study guides (PDF → text extraction)
  2. NSC past exam papers (Grade 10–12)
  3. CAPS curriculum statement documents

These are Crown / Government documents in the public domain.
They provide authoritative, CAPS-aligned content but require PDF parsing.
"""
from __future__ import annotations

import io
import logging
import re
from typing import Any, AsyncIterator

from scripts.ingestion.config import SOURCES
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

# Direct download links for DBE Mind the Gap study guides (public PDF URLs)
_MIND_THE_GAP: list[dict[str, Any]] = [
    # Grade 12 Mind the Gap
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGMathematics2019%20.pdf",
     "subject": "mathematics", "grade": 12, "title": "Mind the Gap Mathematics 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGPhysicalSciences2019.pdf",
     "subject": "physical_sciences", "grade": 12, "title": "Mind the Gap Physical Sciences 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGLifeSciences2019.pdf",
     "subject": "life_sciences", "grade": 12, "title": "Mind the Gap Life Sciences 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGAccounting2019.pdf",
     "subject": "accounting", "grade": 12, "title": "Mind the Gap Accounting 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGBusinessStudies2019.pdf",
     "subject": "business_studies", "grade": 12, "title": "Mind the Gap Business Studies 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGEconomics2019.pdf",
     "subject": "economics", "grade": 12, "title": "Mind the Gap Economics 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGGeography2019.pdf",
     "subject": "geography", "grade": 12, "title": "Mind the Gap Geography 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGHistory2019.pdf",
     "subject": "history", "grade": 12, "title": "Mind the Gap History 2019"},
    {"url": "https://www.education.gov.za/Portals/0/Documents/Publications/Mind%20the%20Gap%202019/MtGEnglishHLLANG2019.pdf",
     "subject": "english_home_language", "grade": 12, "title": "Mind the Gap English HL 2019"},
]

# Past NSC exam paper index pages
_PAST_PAPERS_INDEX: list[dict[str, Any]] = [
    {"url": "https://www.education.gov.za/Curriculum/NationalSeniorCertificate(NSC)Examinations/NSCPastExaminationpapers.aspx",
     "description": "NSC Past Papers Index", "grades": [10, 11, 12]},
]


class DBESouthAfricaScraper(BaseScraper):
    """
    Downloads and extracts text from DBE study guides and past papers.
    Requires `pdfplumber` for PDF extraction.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["dbe"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        # Discover Mind the Gap PDFs dynamically from the DBE index page
        discovered: list[dict[str, Any]] = []
        try:
            discovered = await self._discover_mind_the_gap_links()
        except Exception as exc:  # pragma: no cover - best-effort discovery
            logger.warning("[DBE] Discovery failed: %s", exc)

        docs = [d for d in (discovered or _MIND_THE_GAP)
                if self._within_grade_range(d.get("grade"))]
        self._total = len(docs)
        logger.info("[DBE] Downloading %d Mind the Gap guides", self._total)

        for i, doc in enumerate(docs):
            if self._at_limit():
                break
            self._emit(i, self._total, f"DBE: {doc['title']}")
            item = await self._fetch_pdf_doc(doc)
            if item:
                self._done += 1
                yield item

        # Also scrape the NSC past papers index for paper listings
        async for item in self._scrape_past_papers():
            if self._at_limit():
                return
            yield item

    async def _fetch_pdf_doc(self, doc: dict[str, Any]) -> RawContent | None:
        """Download a PDF and extract text using pdfplumber."""
        try:
            import pdfplumber  # type: ignore
        except ImportError:
            logger.warning("[DBE] pdfplumber not installed — skipping PDF extraction. "
                           "Install with: pip install pdfplumber --break-system-packages")
            return None

        logger.info("[DBE] Downloading: %s", doc["url"])
        # Download raw bytes
        assert self._session is not None
        from scripts.ingestion.utils.robots_checker import can_fetch
        from scripts.ingestion.utils.rate_limiter import throttle
        allowed = await can_fetch(doc["url"], self.config.robots_txt_url)
        if not allowed:
            return None
        await throttle(self.config.id, self.config.rate_limit_rps)

        try:
            async with self._session.get(doc["url"]) as resp:
                if resp.status != 200:
                    logger.warning("[DBE] HTTP %d for %s", resp.status, doc["url"])
                    # Try Wayback CDX API lookup for an archived capture
                    cdx_api = "https://web.archive.org/cdx/search/cdx"
                    params = {
                        "url": doc["url"],
                        "output": "json",
                        "filter": "statuscode:200",
                        "limit": "1",
                    }
                    logger.info("[DBE] Querying Wayback CDX for %s", doc["url"])
                    try:
                        async with self._session.get(cdx_api, params=params) as cdx:
                            if cdx.status == 200:
                                try:
                                    j = await cdx.json()
                                except Exception:
                                    j = None

                                if j and isinstance(j, list) and len(j) > 1:
                                    # Second row is the first capture
                                    row = j[1]
                                    timestamp = row[1]
                                    archived_url = f"https://web.archive.org/web/{timestamp}/{doc['url']}"
                                    logger.info("[DBE] Found Wayback capture: %s", archived_url)
                                    async with self._session.get(archived_url) as cap:
                                        if cap.status == 200:
                                            pdf_bytes = await cap.read()
                                        else:
                                            logger.warning("[DBE] Wayback capture HTTP %d", cap.status)
                                            return None
                                else:
                                    # No CDX JSON result; try Wayback listing page as a fallback
                                    wayback_listing = f"https://web.archive.org/web/*/{doc['url']}"
                                    logger.info("[DBE] No CDX result; checking Wayback listing for %s", doc["url"])
                                    async with self._session.get(wayback_listing) as wb:
                                        if wb.status == 200:
                                            body = await wb.text()
                                            m = re.search(r'href="(https?://web\.archive\.org/web/[^\"]+)"', body)
                                            if m:
                                                capture = m.group(1)
                                                logger.info("[DBE] Found Wayback capture (listing): %s", capture)
                                                async with self._session.get(capture) as cap:
                                                    if cap.status == 200:
                                                        pdf_bytes = await cap.read()
                                                    else:
                                                        logger.warning("[DBE] Wayback capture HTTP %d", cap.status)
                                                        return None
                                            else:
                                                logger.warning("[DBE] No Wayback captures found for %s", doc["url"])
                                                return None
                                        else:
                                            logger.warning("[DBE] Wayback listing HTTP %d", wb.status)
                                            return None
                            else:
                                logger.warning("[DBE] Wayback CDX HTTP %d", cdx.status)
                                return None
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("[DBE] Wayback CDX lookup failed: %s", exc)
                        return None
                pdf_bytes = await resp.read()
        except Exception as exc:  # noqa: BLE001
            logger.error("[DBE] Download failed: %s", exc)
            return None

        # Extract text page by page
        pages: list[dict[str, Any]] = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    if len(text.strip()) > 50:
                        pages.append({"page": page_num, "text": text.strip()})
        except Exception as exc:  # noqa: BLE001
            logger.error("[DBE] PDF parse failed for %s: %s", doc["title"], exc)
            return None

        full_text = "\n\n".join(p["text"] for p in pages)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()

        if len(full_text) < 200:
            return None

        return RawContent(
            source_id          = "dbe",
            source_url         = doc["url"],
            source_internal_id = doc["url"].split("/")[-1],
            raw_text           = full_text,
            raw_json           = {"pages": pages},
            metadata           = {
                "kind":         "textbook_section",
                "title":        doc["title"],
                "subject":      doc["subject"],
                "grade":        doc["grade"],
                "jurisdiction": "za",
                "caps_subject": doc["subject"],
                "doc_type":     "mind_the_gap",
            },
            license  = "Government Open License (ZA)",
            language = "en",
        )

    async def _discover_mind_the_gap_links(self) -> list[dict[str, Any]]:
        """Scrape the DBE 'Mind the Gap' index page and return PDF links.

        Falls back to returning an empty list if discovery fails; the caller
        may choose to fall back to a static list.
        """
        index_url = self.config.extra.get("mind_the_gap") if self.config.extra else None
        if not index_url:
            index_url = f"{self.config.base_url}/Curriculum/LearningandTeachingSupportMaterials(LTSM)/MindtheGap.aspx"

        html = await self._get(index_url)
        if not html or not isinstance(html, str):
            # Some government sites block non-browser user-agents — try
            # again with a common browser UA as a best-effort fallback.
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
            }
            html = await self._get(index_url, headers=headers)
            if not html or not isinstance(html, str):
                logger.info("[DBE] No Mind the Gap index HTML available at %s", index_url)
                return []

        from bs4 import BeautifulSoup  # type: ignore
        from urllib.parse import urljoin

        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.find_all("a", href=re.compile(r"\.pdf", re.I))
        docs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for a in anchors:
            href = a.get("href", "")
            text = a.get_text(strip=True) or ""
            # Heuristics: prefer links that reference 'mind' or have MtG in the filename
            if not re.search(r"mind|mtg|mindthegap", text + href, re.I):
                continue
            pdf_url = urljoin(self.config.base_url, href)
            if pdf_url in seen:
                continue
            seen.add(pdf_url)

            title = text or pdf_url.split("/")[-1]
            t = (text + " " + href).lower()
            subject = "unknown"
            if "math" in t or "mathemat" in t:
                subject = "mathematics"
            elif "physical" in t or "physics" in t:
                subject = "physical_sciences"
            elif "life" in t or "biology" in t:
                subject = "life_sciences"
            elif "account" in t:
                subject = "accounting"
            elif "business" in t:
                subject = "business_studies"
            elif "economic" in t:
                subject = "economics"
            elif "geograph" in t:
                subject = "geography"
            elif "history" in t:
                subject = "history"
            elif "english" in t:
                subject = "english_home_language"

            docs.append({
                "url": pdf_url,
                "title": title,
                "subject": subject,
                "grade": 12,
            })

        return docs

    async def _scrape_past_papers(self) -> AsyncIterator[RawContent]:
        """Fetch NSC past paper listing and extract PDF links."""
        for index in _PAST_PAPERS_INDEX:
            html = await self._get(index["url"])
            if not html or not isinstance(html, str):
                continue
            from bs4 import BeautifulSoup
            soup  = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=re.compile(r"\.pdf", re.I))
            logger.info("[DBE] Found %d past paper links on index page", len(links))
            for a in links[:50]:   # cap to first 50 papers
                if self._at_limit():
                    return
                href     = a.get("href", "")
                from urllib.parse import urljoin
                pdf_url  = urljoin(self.config.base_url, href)
                text     = a.get_text(strip=True)
                meta     = self._classify_past_paper(text, pdf_url)
                if not meta or not self._within_grade_range(meta.get("grade")):
                    continue
                item = await self._fetch_pdf_doc({
                    "url": pdf_url, "title": text, **meta
                })
                if item:
                    self._done += 1
                    yield item

    @staticmethod
    def _classify_past_paper(title: str, url: str) -> dict[str, Any] | None:
        """Extract subject and grade from a paper filename/title."""
        t = title.lower()
        g = None
        for grade in range(10, 13):
            if f"grade {grade}" in t or f"gr{grade}" in t or f"gr {grade}" in t:
                g = grade
                break
        subject = "unknown"
        if "math" in t:        subject = "mathematics"
        elif "physics" in t:   subject = "physical_sciences"
        elif "biology" in t or "life" in t: subject = "life_sciences"
        elif "english" in t:   subject = "english_home_language"
        elif "history" in t:   subject = "history"
        elif "geography" in t: subject = "geography"
        elif "accounting" in t:subject = "accounting"
        elif "economics" in t: subject = "economics"
        if g and subject != "unknown":
            return {"subject": subject, "grade": g}
        return None
