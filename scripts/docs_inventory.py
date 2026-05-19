#!/usr/bin/env python3
"""Inventory EduBoost documentation and plan higher-level documentation outputs.

The default path is intentionally dependency-light: crawl local repository
documentation, extract structure and risk signals, then emit generated JSON and
Markdown artifacts. Optional converters can be enabled for binary documents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "generated" / "documentation_intelligence"
DEFAULT_SOURCE_ROOTS = (
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "TODO.md",
    "RoadMap.md",
    "mkdocs.yml",
    "docs",
    "audits",
    "reports",
    "k8s",
    "phases",
    "data/synthetic",
)
TEXT_EXTENSIONS = {
    ".adoc",
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".mdx",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
BINARY_DOCUMENT_EXTENSIONS = {".docx", ".pdf", ".pptx", ".xlsx"}
DOCUMENT_EXTENSIONS = TEXT_EXTENSIONS | BINARY_DOCUMENT_EXTENSIONS
EXCLUDED_DIRS = {
    ".git",
    ".hypothesis",
    ".import_linter_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "coverage_html",
    "node_modules",
    "site",
    "temp",
}
GENERATED_OUTPUT_PARTS = ("docs", "generated", "documentation_intelligence")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RAW_URL_RE = re.compile(r"https?://[^\s)>\"']+")
LOCAL_PATH_RE = re.compile(
    r"\b(?:docs|audits|scripts|tests|app|requirements|reports|k8s|docker|data|phases)/"
    r"[A-Za-z0-9_./-]+\.(?:adoc|csv|docx|json|md|mdx|pdf|pptx|py|rst|txt|xlsx|ya?ml)\b"
)
DATE_RE = re.compile(r"\b(?:20\d{2}|19\d{2})[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])\b")
STATUS_PATTERNS: dict[str, re.Pattern[str]] = {
    "todo": re.compile(r"\bTODO\b|to do|outstanding", re.IGNORECASE),
    "draft": re.compile(r"\bDRAFT\b|\bWIP\b|work in progress", re.IGNORECASE),
    "blocked": re.compile(r"\bBLOCKED\b|blocker|cannot proceed", re.IGNORECASE),
    "needs_review": re.compile(r"needs review|review required|pending review", re.IGNORECASE),
    "ready": re.compile(r"\bREADY\b|ready for|production ready|release ready", re.IGNORECASE),
    "pass": re.compile(r"\bPASS\b|\bGREEN\b|passing", re.IGNORECASE),
    "fail": re.compile(r"\bFAIL\b|\bRED\b|failing|failed", re.IGNORECASE),
}
EVIDENCE_RE = re.compile(
    r"evidence|proof|audit|manifest|attestation|checklist|contract|report|readiness|signoff|gate",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CandidateDocument:
    title: str
    output_path: str
    description: str
    source_categories: tuple[str, ...]
    preferred_artifact: str
    preferred_skill: str


HIGHER_LEVEL_DOCUMENTS = (
    CandidateDocument(
        "System Overview",
        "docs/generated/documentation_intelligence/system_overview.md",
        "A concise executive and technical overview of EduBoost V2's purpose, runtime shape, and current delivery state.",
        ("general", "architecture", "audit_review"),
        "Markdown / MkDocs page",
        "Local repo crawler plus retrieval index",
    ),
    CandidateDocument(
        "Architecture Handoff",
        "docs/generated/documentation_intelligence/architecture_handoff.md",
        "A handoff pack for developers and agents covering services, routers, boundaries, and architecture decisions.",
        ("architecture", "api_reference", "database"),
        "Markdown, then DOCX when formal handoff is needed",
        "documents:documents",
    ),
    CandidateDocument(
        "Production Readiness Report",
        "docs/generated/documentation_intelligence/production_readiness_report.md",
        "A readiness summary grounded in deployment, operations, security, release, and evidence documentation.",
        ("deployment", "operations_support", "security_privacy", "release_evidence"),
        "DOCX report and Markdown source",
        "documents:documents",
    ),
    CandidateDocument(
        "Roadmap Consolidation",
        "docs/generated/documentation_intelligence/roadmap_consolidation.md",
        "A deduplicated roadmap that reconciles active tasks, outstanding items, and implementation reports.",
        ("roadmap", "audit_review"),
        "Markdown and spreadsheet backlog",
        "spreadsheets:Spreadsheets",
    ),
    CandidateDocument(
        "Audit Evidence Index",
        "docs/generated/documentation_intelligence/audit_evidence_index.md",
        "A navigable index of evidence documents, contracts, manifests, release packets, and proof records.",
        ("audit_review", "release_evidence", "security_privacy"),
        "Markdown index and XLSX evidence matrix",
        "spreadsheets:Spreadsheets",
    ),
    CandidateDocument(
        "Developer Onboarding Guide",
        "docs/generated/documentation_intelligence/developer_onboarding_guide.md",
        "A practical guide for setup, commands, docs workflow, API references, and common development loops.",
        ("onboarding_development", "api_reference", "general"),
        "MkDocs page",
        "Local repo crawler plus retrieval index",
    ),
    CandidateDocument(
        "API Documentation Index",
        "docs/generated/documentation_intelligence/api_documentation_index.md",
        "A gateway into OpenAPI, router inventory, service references, and runtime contracts.",
        ("api_reference", "architecture"),
        "MkDocs page",
        "Local repo crawler plus retrieval index",
    ),
    CandidateDocument(
        "POPIA Compliance Pack",
        "docs/generated/documentation_intelligence/popia_compliance_pack.md",
        "A formal privacy/compliance packet from POPIA, consent, legal, security, and subprocessors documentation.",
        ("compliance_popia", "security_privacy"),
        "DOCX report and XLSX control matrix",
        "documents:documents + spreadsheets:Spreadsheets",
    ),
    CandidateDocument(
        "Beta Launch Pack",
        "docs/generated/documentation_intelligence/beta_launch_pack.md",
        "A launch-readiness bundle covering scope, acceptance criteria, known issues, feedback intake, and exit criteria.",
        ("beta_launch",),
        "DOCX pack and presentation summary",
        "documents:documents + presentations:Presentations",
    ),
    CandidateDocument(
        "CAPS Content Coverage Pack",
        "docs/generated/documentation_intelligence/caps_content_coverage_pack.md",
        "A content and learning-science pack for CAPS matrices, item review, mastery, IRT, and lesson coverage.",
        ("caps_content", "learning_science", "ai_ml"),
        "XLSX coverage matrix and Markdown narrative",
        "spreadsheets:Spreadsheets",
    ),
)


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_generated_output(path: Path) -> bool:
    parts = path.relative_to(REPO_ROOT).parts if path.is_relative_to(REPO_ROOT) else path.parts
    return GENERATED_OUTPUT_PARTS == parts[: len(GENERATED_OUTPUT_PARTS)]


def should_skip_dir(path: Path) -> bool:
    return path.name in EXCLUDED_DIRS or is_generated_output(path)


def discover_documents(source_roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for source in source_roots:
        path = (REPO_ROOT / source).resolve()
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in DOCUMENT_EXTENSIONS:
            files.append(path)
            continue
        if not path.is_dir():
            continue
        for current, dirs, names in os.walk(path):
            current_path = Path(current)
            dirs[:] = [name for name in dirs if not should_skip_dir(current_path / name)]
            for name in names:
                candidate = current_path / name
                if candidate.suffix.lower() in DOCUMENT_EXTENSIONS and not is_generated_output(candidate):
                    files.append(candidate.resolve())
    return sorted(set(files), key=lambda item: relative(item))


def read_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except Exception:
        return ""

    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return ""

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        pieces = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        text = unescape("".join(pieces).strip())
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def convert_with_markitdown(path: Path) -> str:
    from markitdown import MarkItDown  # type: ignore[import-not-found]

    result = MarkItDown().convert(str(path))
    return getattr(result, "text_content", "") or ""


def convert_with_docling(path: Path) -> str:
    from docling.document_converter import DocumentConverter  # type: ignore[import-not-found]

    result = DocumentConverter().convert(str(path))
    return result.document.export_to_markdown()


def read_text(path: Path, converter: str) -> tuple[str, str | None]:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        try:
            return path.read_text(encoding="utf-8"), None
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="replace"), None
    if suffix == ".docx" and converter == "none":
        text = read_docx_text(path)
        return text, None if text else "No text extracted from DOCX."
    if converter in {"markitdown", "auto"}:
        try:
            return convert_with_markitdown(path), None
        except Exception as exc:  # noqa: BLE001 - optional converter path
            if converter == "markitdown":
                return "", f"MarkItDown conversion failed: {exc}"
    if converter in {"docling", "auto"}:
        try:
            return convert_with_docling(path), None
        except Exception as exc:  # noqa: BLE001 - optional converter path
            if converter == "docling":
                return "", f"Docling conversion failed: {exc}"
    return "", None if suffix not in BINARY_DOCUMENT_EXTENSIONS else "Binary document not converted."


def extract_front_matter_title(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    front_matter = text[4:end]
    for line in front_matter.splitlines():
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def clean_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().strip("#")).strip()


def extract_headings(text: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": clean_heading(match.group(2)),
                    "line": line_no,
                }
            )
    return headings


def extract_title(path: Path, text: str, headings: list[dict[str, Any]]) -> str:
    front_matter_title = extract_front_matter_title(text)
    if front_matter_title:
        return front_matter_title
    for heading in headings:
        if heading["level"] == 1:
            return heading["text"]
    if headings:
        return headings[0]["text"]
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("{", "[", "---")):
            return clean_heading(stripped)[:120]
    return path.stem.replace("_", " ").replace("-", " ").title()


def classify(path: Path, title: str, text: str) -> str:
    rel = relative(path).lower()
    title_text = f"{title}\n{text[:4000]}".lower()
    checks: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("compliance_popia", ("popia", "privacy", "consent", "subprocessor", "erasure", "legal")),
        ("beta_launch", ("beta", "launch", "cohort", "feedback", "acceptance criteria")),
        ("release_evidence", ("release", "evidence", "signoff", "attestation", "seal", "closeout")),
        ("deployment", ("deployment", "docker", "staging", "rollback", "artifact", "environment")),
        ("operations_support", ("operations", "incident", "runbook", "sla", "support", "on call", "backup", "restore")),
        ("security_privacy", ("security", "secret", "threat", "hardening", "auth", "rbac")),
        ("database", ("database", "migration", "schema", "repository", "transaction")),
        ("api_reference", ("api", "openapi", "router", "endpoint", "fastapi", "route")),
        ("architecture", ("architecture", "boundary", "service", "dependency", "adr", "diagram")),
        ("roadmap", ("roadmap", "todo", "active_tasks", "implementation epic", "execution plan")),
        ("audit_review", ("audit", "review", "assessment", "findings", "technical report")),
        ("caps_content", ("caps", "grade4", "lesson", "item review", "coverage matrix")),
        ("learning_science", ("learning science", "mastery", "irt", "learning evidence")),
        ("ai_ml", ("llm", "ai", "model", "inference", "training", "prompt")),
        ("onboarding_development", ("development", "contributing", "readme", "setup", "makefile")),
        ("kubernetes_infra", ("k8s", "kubernetes", "aks")),
    )
    haystack = f"{rel}\n{title_text}"
    for category, keywords in checks:
        if any(keyword in haystack for keyword in keywords):
            return category
    return "general"


def line_number_for(text: str, needle: str) -> int | None:
    if not needle:
        return None
    for line_no, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return line_no
    return None


def resolve_local_link(source: Path, target: str) -> tuple[str, bool | None]:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "mailto"} or target.startswith("#"):
        return target, None
    clean_target = unquote(target.split("#", 1)[0]).strip()
    if not clean_target:
        return target, None
    if clean_target.startswith("/"):
        candidate = REPO_ROOT / clean_target.lstrip("/")
    else:
        candidate = source.parent / clean_target
    return clean_target, candidate.exists()


def extract_links(path: Path, text: str) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    seen: set[tuple[str, int | None]] = set()

    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(1).strip("<>")
        line_no = line_number_for(text, match.group(0))
        normalized, exists = resolve_local_link(path, target)
        key = (target, line_no)
        if key not in seen:
            links.append(
                {
                    "target": target,
                    "normalized_target": normalized,
                    "line": line_no,
                    "kind": "external" if target.startswith(("http://", "https://")) else "local",
                    "exists": exists,
                }
            )
            seen.add(key)

    for match in RAW_URL_RE.finditer(text):
        target = match.group(0).rstrip(".,")
        line_no = line_number_for(text, target)
        key = (target, line_no)
        if key not in seen:
            links.append(
                {
                    "target": target,
                    "normalized_target": target,
                    "line": line_no,
                    "kind": "external",
                    "exists": None,
                }
            )
            seen.add(key)
    return links


def extract_local_path_references(text: str) -> list[str]:
    return sorted(set(match.group(0) for match in LOCAL_PATH_RE.finditer(text)))


def extract_statuses(text: str) -> list[str]:
    return [name for name, pattern in STATUS_PATTERNS.items() if pattern.search(text)]


def extract_dates(text: str) -> list[str]:
    normalized = [match.group(0).replace("/", "-") for match in DATE_RE.finditer(text)]
    return sorted(set(normalized))


def extract_evidence_references(links: list[dict[str, Any]], local_paths: list[str]) -> list[str]:
    references: set[str] = set()
    for link in links:
        target = link["normalized_target"]
        if EVIDENCE_RE.search(target):
            references.add(target)
    for path in local_paths:
        if EVIDENCE_RE.search(path):
            references.add(path)
    return sorted(references)[:40]


def mkdocs_nav_paths() -> set[str]:
    config = REPO_ROOT / "mkdocs.yml"
    if not config.exists():
        return set()
    text = config.read_text(encoding="utf-8", errors="replace")
    paths = {
        match.group(1)
        for match in re.finditer(r":\s+([A-Za-z0-9_./-]+\.md)\s*$", text, flags=re.MULTILINE)
    }
    return {f"docs/{path}" for path in paths}


def inventory_document(path: Path, converter: str) -> dict[str, Any]:
    text, conversion_error = read_text(path, converter)
    headings = extract_headings(text)
    title = extract_title(path, text, headings)
    links = extract_links(path, text)
    local_paths = extract_local_path_references(text)
    stat = path.stat()
    modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    evidence_references = extract_evidence_references(links, local_paths)
    statuses = extract_statuses(text)
    return {
        "path": relative(path),
        "format": path.suffix.lower().lstrip(".") or "unknown",
        "category": classify(path, title, text),
        "title": title,
        "headings": headings[:80],
        "heading_count": len(headings),
        "links": links,
        "local_path_references": local_paths[:80],
        "status_signals": statuses,
        "dates": extract_dates(text)[:40],
        "evidence_references": evidence_references,
        "word_count": len(re.findall(r"\b\w+\b", text)),
        "line_count": len(text.splitlines()),
        "size_bytes": stat.st_size,
        "modified_date": modified_at.date().isoformat(),
        "sha256": sha256(path),
        "conversion_error": conversion_error,
    }


def stale_cutoff_date(stale_days: int) -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - (
        stale_days * datetime.resolution
    )


def compute_gaps(documents: list[dict[str, Any]], stale_days: int) -> dict[str, list[str]]:
    nav_paths = mkdocs_nav_paths()
    now = datetime.now(timezone.utc)
    stale_paths: list[str] = []
    for document in documents:
        modified = datetime.fromisoformat(document["modified_date"]).replace(tzinfo=timezone.utc)
        if (now - modified).days > stale_days:
            stale_paths.append(document["path"])

    duplicate_titles = [
        title
        for title, count in Counter(document["title"] for document in documents).items()
        if count > 1
    ]
    broken_links: list[str] = []
    for document in documents:
        for link in document["links"]:
            if link["kind"] == "local" and link["exists"] is False:
                broken_links.append(f"{document['path']}:{link.get('line') or '?'} -> {link['target']}")

    docs_markdown = [document["path"] for document in documents if document["path"].startswith("docs/") and document["format"] == "md"]
    return {
        "missing_title": [document["path"] for document in documents if not document["title"]],
        "no_headings": [document["path"] for document in documents if document["heading_count"] == 0],
        "unresolved_status_signals": [
            document["path"]
            for document in documents
            if set(document["status_signals"]) & {"todo", "draft", "blocked", "needs_review", "fail"}
        ],
        "stale_documents": stale_paths,
        "broken_local_links": sorted(broken_links),
        "duplicate_titles": sorted(duplicate_titles),
        "docs_markdown_not_in_mkdocs_nav": sorted(path for path in docs_markdown if path not in nav_paths),
        "binary_documents_without_text": [
            document["path"]
            for document in documents
            if document["format"] in {"pdf", "pptx", "xlsx"} and document["word_count"] == 0
        ],
    }


def candidate_plan(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_category: dict[str, list[str]] = {}
    for document in documents:
        by_category.setdefault(document["category"], []).append(document["path"])

    plan: list[dict[str, Any]] = []
    for candidate in HIGHER_LEVEL_DOCUMENTS:
        sources: list[str] = []
        for category in candidate.source_categories:
            sources.extend(by_category.get(category, [])[:12])
        plan.append(
            {
                "title": candidate.title,
                "output_path": candidate.output_path,
                "description": candidate.description,
                "source_categories": list(candidate.source_categories),
                "source_count": len(sources),
                "example_sources": sorted(set(sources))[:20],
                "preferred_artifact": candidate.preferred_artifact,
                "preferred_skill": candidate.preferred_skill,
            }
        )
    return plan


def build_inventory(source_roots: list[str], converter: str, stale_days: int) -> dict[str, Any]:
    documents = [inventory_document(path, converter) for path in discover_documents(source_roots)]
    category_counts = dict(sorted(Counter(document["category"] for document in documents).items()))
    status_counts = dict(sorted(Counter(signal for document in documents for signal in document["status_signals"]).items()))
    format_counts = dict(sorted(Counter(document["format"] for document in documents).items()))
    gaps = compute_gaps(documents, stale_days)
    return {
        "schema_version": 1,
        "source_roots": source_roots,
        "converter": converter,
        "files_scanned": len(documents),
        "format_counts": format_counts,
        "category_counts": category_counts,
        "status_counts": status_counts,
        "gap_counts": {name: len(items) for name, items in sorted(gaps.items())},
        "gaps": gaps,
        "higher_level_document_candidates": candidate_plan(documents),
        "documents": documents,
    }


def markdown_table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def render_inventory_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# Documentation Inventory",
        "",
        "> Generated by `scripts/docs_inventory.py`. Do not edit manually.",
        "",
        "## Summary",
        "",
        f"- Files scanned: {inventory['files_scanned']}",
        f"- Converter: `{inventory['converter']}`",
        f"- Formats: {', '.join(f'`{key}`={value}' for key, value in inventory['format_counts'].items())}",
        f"- Categories: {', '.join(f'`{key}`={value}' for key, value in inventory['category_counts'].items())}",
        f"- Gap counts: {', '.join(f'`{key}`={value}' for key, value in inventory['gap_counts'].items())}",
        "",
        "## Documents",
        "",
        "| Path | Category | Title | Status Signals | Dates | Evidence Refs | Links |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for document in inventory["documents"]:
        lines.append(
            markdown_table_row(
                [
                    f"`{document['path']}`",
                    document["category"],
                    document["title"],
                    ", ".join(document["status_signals"]) or "-",
                    ", ".join(document["dates"][:4]) or "-",
                    str(len(document["evidence_references"])),
                    str(len(document["links"])),
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_gap_report(inventory: dict[str, Any]) -> str:
    lines = [
        "# Documentation Gap Report",
        "",
        "> Generated by `scripts/docs_inventory.py`. Do not edit manually.",
        "",
        "## Gap Summary",
        "",
    ]
    for name, count in inventory["gap_counts"].items():
        lines.append(f"- `{name}`: {count}")
    lines.append("")
    for name, items in inventory["gaps"].items():
        lines.extend([f"## {name.replace('_', ' ').title()}", ""])
        if not items:
            lines.extend(["No items found.", ""])
            continue
        for item in items[:200]:
            lines.append(f"- `{item}`")
        if len(items) > 200:
            lines.append(f"- ... {len(items) - 200} more")
        lines.append("")
    return "\n".join(lines)


def render_generation_plan(inventory: dict[str, Any]) -> str:
    lines = [
        "# Documentation Generation Plan",
        "",
        "> Generated by `scripts/docs_inventory.py`. Do not edit manually.",
        "",
        "Use this plan to turn the raw documentation corpus into higher-level deliverables.",
        "",
        "## Pipeline",
        "",
        "1. Discover repository files with `scripts/docs_inventory.py`.",
        "2. Convert non-Markdown artifacts with MarkItDown for lightweight ingestion or Docling for richer layout/table extraction.",
        "3. Build a retrieval index from `docs_inventory.json` plus converted Markdown chunks.",
        "4. Generate targeted documents from the candidate list below, citing source paths from the inventory.",
        "5. Render final artifacts with the Documents, Presentations, or Spreadsheets skills when a `.docx`, `.pptx`, or `.xlsx` deliverable is needed.",
        "",
        "## Candidate Documents",
        "",
    ]
    for candidate in inventory["higher_level_document_candidates"]:
        lines.extend(
            [
                f"### {candidate['title']}",
                "",
                f"- Output: `{candidate['output_path']}`",
                f"- Purpose: {candidate['description']}",
                f"- Preferred artifact: {candidate['preferred_artifact']}",
                f"- Preferred skill: `{candidate['preferred_skill']}`",
                f"- Matching source count: {candidate['source_count']}",
                "- Example sources:",
            ]
        )
        if candidate["example_sources"]:
            for source in candidate["example_sources"][:12]:
                lines.append(f"  - `{source}`")
        else:
            lines.append("  - No matching sources found yet.")
        lines.append("")
    return "\n".join(lines)


def output_payloads(inventory: dict[str, Any]) -> dict[str, str]:
    return {
        "docs_inventory.json": json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        "docs_inventory.md": render_inventory_markdown(inventory),
        "docs_gap_report.md": render_gap_report(inventory),
        "docs_generation_plan.md": render_generation_plan(inventory),
    }


def write_outputs(output_dir: Path, payloads: dict[str, str], check: bool) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    if check:
        missing: list[str] = []
        stale: list[str] = []
        for filename, content in payloads.items():
            path = output_dir / filename
            if not path.exists():
                missing.append(str(path))
                continue
            if path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
        if missing or stale:
            for path in missing:
                print(f"missing generated docs inventory artifact: {path}", file=sys.stderr)
            for path in stale:
                print(f"stale generated docs inventory artifact: {path}", file=sys.stderr)
            print("Run `python3 scripts/docs_inventory.py` to refresh.", file=sys.stderr)
            return 1
        print("Documentation inventory artifacts are current.")
        return 0

    for filename, content in payloads.items():
        (output_dir / filename).write_text(content, encoding="utf-8")
    for filename in payloads:
        print(output_dir / filename)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        action="append",
        dest="source_roots",
        help="Source root to crawl. May be repeated. Defaults to common EduBoost docs roots.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated inventory artifacts.",
    )
    parser.add_argument(
        "--converter",
        choices=("none", "markitdown", "docling", "auto"),
        default="none",
        help="Optional converter for binary documents. Default keeps the base run dependency-free.",
    )
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--check", action="store_true", help="Fail if generated artifacts are missing or stale.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_roots = args.source_roots or list(DEFAULT_SOURCE_ROOTS)
    inventory = build_inventory(source_roots=source_roots, converter=args.converter, stale_days=args.stale_days)
    payloads = output_payloads(inventory)
    return write_outputs(Path(args.output_dir), payloads, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
