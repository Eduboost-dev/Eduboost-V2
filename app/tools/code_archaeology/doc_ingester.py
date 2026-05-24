"""
doc_ingester.py  v4
-------------------
Scans a repository for tracking / planning / audit documents and extracts
their content for later synthesis.

New in v4
─────────
• DocHealthScore  — composite freshness × completeness × coverage score (0–100)
• GlossaryExtractor  — pulls capitalised acronyms + domain terms from all docs
• EnhancedDependencyGraph  — weighted edges (count of cross-references)
• DocCluster  — groups docs by thematic similarity (shared section headings)
• ObsolescenceSignal  — detects stale docs (no git touch in N days, old dates)
• Everything from v3 preserved (no regressions)
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ── Known high-value paths ────────────────────────────────────────────────────

TRACKING_SUBPATHS = {
    "docs/current_state.md",
    "docs/project_status.md",
    "docs/POPIA_COMPLIANCE.md",
    "docs/v2_migration.md",
    "docs/architecture/V2_ARCHITECTURE.md",
    "docs/caps/grade4_maths_coverage_matrix.md",
    "docs/caps/grade4_maths_120_item_production_plan.md",
    "CHANGELOG.md",
    "TODO.md",
    "RoadMap.md",
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "PR_INTEGRATION_SUMMARY.md",
    "OUTSTANDING_TODO_ITEMS.md.bak",
    "task_matrix.csv",
    "docs/openapi.json",
}

AUDIT_DIR_NAMES = {"audits", "reports", "phases", "docs", "artifacts"}
MARKDOWN_EXTS   = {".md", ".markdown", ".mdown"}
RST_EXTS        = {".rst"}
ADOC_EXTS       = {".adoc", ".asciidoc"}
NOTEBOOK_EXTS   = {".ipynb"}

# ── Sentiment ──────────────────────────────────────────────────────────────────

_POSITIVE_KW = {
    "complete", "done", "shipped", "merged", "deployed", "pass", "green",
    "success", "ready", "stable", "improved", "fixed", "optimised", "optimized",
}
_RISK_KW = {
    "blocked", "broken", "fail", "error", "critical", "urgent", "regression",
    "security", "vulnerability", "leak", "corrupt", "missing", "todo", "fixme",
    "hack", "debt", "warning", "deprecated", "outstanding",
}


def _sentiment_score(text: str) -> dict:
    words = re.findall(r"\b\w+\b", text.lower())
    pos  = sum(1 for w in words if w in _POSITIVE_KW)
    risk = sum(1 for w in words if w in _RISK_KW)
    total = len(words) or 1
    return {
        "positive": round(pos / total, 4),
        "risk":     round(risk / total, 4),
        "tone":     "positive" if pos > risk else ("risk" if risk > pos else "neutral"),
    }


# ── Annotation extraction ──────────────────────────────────────────────────────

_ANNOTATION_RE = re.compile(
    r"(?:#|//|<!--)\s*(TODO|FIXME|HACK|NOTE|XXX|WARN)[\s:]*(.*?)(?:-->)?$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class InlineAnnotation:
    kind: str
    text: str
    line: int


def _extract_annotations(content: str) -> list[InlineAnnotation]:
    result = []
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        m = _ANNOTATION_RE.search(line)
        if m:
            result.append(InlineAnnotation(kind=m.group(1).upper(), text=m.group(2).strip(), line=i))
    return result


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class DocSection:
    heading: str
    level: int
    start_line: int
    end_line: int
    content: str
    word_count: int
    anchor: str = ""


@dataclass
class DocHealthScore:
    """Composite health score (0–100) for a tracking document."""
    total: float                    = 0.0
    freshness: float                = 0.0   # 0–33: days since last git touch
    completeness: float             = 0.0   # 0–34: task completion ratio
    coverage: float                 = 0.0   # 0–33: section density vs word count
    is_stale: bool                  = False
    stale_reason: str               = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrackingDoc:
    path: str
    doc_type: str
    title: str
    raw_content: str
    metadata: dict
    sections: list[DocSection]          = field(default_factory=list)
    frontmatter: dict                   = field(default_factory=dict)
    word_count: int                     = 0
    reading_time_min: float             = 0.0
    last_git_modified: Optional[str]    = None
    content_hash: str                   = ""
    links: list[str]                    = field(default_factory=list)
    annotations: list[InlineAnnotation] = field(default_factory=list)
    sentiment: dict                     = field(default_factory=dict)
    referenced_docs: list[str]          = field(default_factory=list)
    notebook_cells: list[dict]          = field(default_factory=list)
    health: DocHealthScore              = field(default_factory=DocHealthScore)  # v4

    def to_dict(self) -> dict:
        d = asdict(self)
        d["sections"]    = [asdict(s) for s in self.sections]
        d["annotations"] = [asdict(a) for a in self.annotations]
        d["health"]      = self.health.to_dict()
        return d


@dataclass
class DocDiff:
    path: str
    added_sections: list[str]   = field(default_factory=list)
    removed_sections: list[str] = field(default_factory=list)
    changed_sections: list[str] = field(default_factory=list)
    completion_delta: float     = 0.0
    word_count_delta: int       = 0
    hash_changed: bool          = False

    def to_dict(self) -> dict:
        return asdict(self)

    
def diff_doc(old: TrackingDoc, new: TrackingDoc) -> DocDiff:
    old_headings = {s.heading: s for s in old.sections}
    new_headings = {s.heading: s for s in new.sections}
    added   = [h for h in new_headings if h not in old_headings]
    removed = [h for h in old_headings if h not in new_headings]
    changed = [h for h in old_headings if h in new_headings and old_headings[h].content != new_headings[h].content]
    old_pct = old.metadata.get("completion_pct", 0.0)
    new_pct = new.metadata.get("completion_pct", 0.0)
    return DocDiff(
        path=new.path, added_sections=added, removed_sections=removed,
        changed_sections=changed, completion_delta=round(new_pct - old_pct, 2),
        word_count_delta=new.word_count - old.word_count,
        hash_changed=old.content_hash != new.content_hash,
    )


# ── AnchorMap ─────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


class AnchorMap:
    def __init__(self, docs: list[TrackingDoc]) -> None:
        self._index: dict[str, list[tuple[str, DocSection]]] = defaultdict(list)
        for doc in docs:
            for sec in doc.sections:
                self._index[sec.anchor].append((doc.path, sec))
                self._index[sec.heading.lower()].append((doc.path, sec))

    def resolve(self, query: str) -> list[dict]:
        key = _slugify(query)
        hits = self._index.get(key) or self._index.get(query.lower(), [])
        return [{"doc": p, "heading": s.heading, "anchor": s.anchor, "level": s.level} for p, s in hits]


# ── v4: Glossary extraction ───────────────────────────────────────────────────

_ACRONYM_RE = re.compile(r"\b([A-Z]{2,}(?:-[A-Z0-9]+)*)\b")
_DEFINED_TERM_RE = re.compile(r"\*\*([A-Za-z][A-Za-z\s]{2,})\*\*\s*[:\-–]")


@dataclass
class GlossaryEntry:
    term: str
    frequency: int
    source_docs: list[str]
    context_sample: str = ""


def build_glossary(docs: list[TrackingDoc]) -> list[GlossaryEntry]:
    """Extract capitalised acronyms and bolded defined terms across all docs."""
    term_freq: Counter = Counter()
    term_docs: dict[str, set[str]] = defaultdict(set)
    term_ctx: dict[str, str] = {}

    for doc in docs:
        text = doc.raw_content
        for m in _ACRONYM_RE.finditer(text):
            term = m.group(1)
            if len(term) < 2 or term in {"HTTP", "URL", "JSON", "YAML", "API", "CI", "CD", "PR", "ID"}:
                continue
            term_freq[term] += 1
            term_docs[term].add(doc.path)
            if term not in term_ctx:
                start = max(0, m.start() - 40)
                term_ctx[term] = text[start: m.end() + 60].replace("\n", " ").strip()

        for m in _DEFINED_TERM_RE.finditer(text):
            term = m.group(1).strip()
            term_freq[term] += 1
            term_docs[term].add(doc.path)
            if term not in term_ctx:
                start = max(0, m.start() - 20)
                term_ctx[term] = text[start: m.end() + 80].replace("\n", " ").strip()

    return [
        GlossaryEntry(
            term=term, frequency=freq,
            source_docs=list(term_docs[term]),
            context_sample=term_ctx.get(term, ""),
        )
        for term, freq in term_freq.most_common(100)
        if freq >= 2
    ]


# ── v4: Enhanced dependency graph (weighted) ──────────────────────────────────

def build_dependency_graph(docs: list[TrackingDoc]) -> dict[str, list[dict]]:
    """Returns {doc_path: [{target, weight}]} weighted by number of references."""
    all_names = {Path(d.path).name.lower(): d.path for d in docs}
    all_stems = {Path(d.path).stem.lower(): d.path for d in docs}
    graph: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for doc in docs:
        link_targets: list[str] = doc.links
        for link in link_targets:
            link_lower = link.lower()
            target_path = None
            for name, path in all_names.items():
                if name in link_lower:
                    target_path = path
                    break
            if not target_path:
                for stem, path in all_stems.items():
                    if stem in link_lower:
                        target_path = path
                        break
            if target_path and target_path != doc.path:
                graph[doc.path][target_path] += 1

    return {
        src: [{"target": tgt, "weight": w} for tgt, w in targets.items()]
        for src, targets in graph.items()
    }


# ── v4: DocHealthScore computation ───────────────────────────────────────────

def _compute_health(doc: TrackingDoc) -> DocHealthScore:
    score = DocHealthScore()

    # Freshness (0–33): penalise docs not touched in > 30 days
    stale_reason = ""
    freshness = 33.0
    if doc.last_git_modified:
        try:
            last = datetime.fromisoformat(doc.last_git_modified.replace("Z", "+00:00"))
            age_days = (datetime.now(tz=last.tzinfo) - last).days
            if age_days > 180:
                freshness = 0.0
                stale_reason = f"Not touched in {age_days} days"
            elif age_days > 90:
                freshness = 11.0
                stale_reason = f"Stale ({age_days}d)"
            elif age_days > 30:
                freshness = 22.0
            # else full 33
        except Exception:
            freshness = 16.0
    else:
        freshness = 8.0
        stale_reason = "No git history found"

    # Completeness (0–34): task completion ratio
    total_tasks = doc.metadata.get("total_tasks", 0)
    done_tasks  = doc.metadata.get("task_done", 0)
    if total_tasks > 0:
        ratio = done_tasks / total_tasks
        completeness = round(ratio * 34, 1)
    elif doc.word_count > 500:
        completeness = 20.0   # no tasks but substantial content
    else:
        completeness = 5.0

    # Coverage (0–33): section count × word density
    section_count = len(doc.sections)
    coverage = min(33.0, round((section_count * 2) + (min(doc.word_count, 3000) / 3000 * 20), 1))

    total = round(freshness + completeness + coverage, 1)
    return DocHealthScore(
        total=total,
        freshness=freshness,
        completeness=completeness,
        coverage=coverage,
        is_stale=bool(stale_reason),
        stale_reason=stale_reason,
    )


# ── v4: DocCluster ───────────────────────────────────────────────────────────

@dataclass
class DocCluster:
    cluster_id: str
    theme: str
    doc_paths: list[str]
    shared_headings: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def cluster_docs(docs: list[TrackingDoc]) -> list[DocCluster]:
    """Group docs by shared section headings (Jaccard similarity ≥ 0.25)."""
    heading_sets = {d.path: {s.heading.lower() for s in d.sections} for d in docs}
    visited: set[str] = set()
    clusters: list[DocCluster] = []
    doc_paths = [d.path for d in docs]

    for i, path_a in enumerate(doc_paths):
        if path_a in visited:
            continue
        group = [path_a]
        shared_all = heading_sets.get(path_a, set())
        for path_b in doc_paths[i + 1:]:
            if path_b in visited:
                continue
            set_a = heading_sets.get(path_a, set())
            set_b = heading_sets.get(path_b, set())
            if not set_a or not set_b:
                continue
            jaccard = len(set_a & set_b) / len(set_a | set_b)
            if jaccard >= 0.25:
                group.append(path_b)
                visited.add(path_b)
                shared_all &= set_b
        if len(group) >= 2:
            shared = sorted(shared_all)[:5]
            theme = shared[0] if shared else Path(path_a).stem
            clusters.append(DocCluster(
                cluster_id=f"cluster-{len(clusters)+1}",
                theme=theme,
                doc_paths=group,
                shared_headings=shared,
            ))
            visited.add(path_a)

    return clusters
