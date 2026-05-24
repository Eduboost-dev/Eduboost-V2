"""
sync_engine.py  v3
------------------
Correlates git commit history with tracking documents to produce a unified,
richly-annotated timeline.  For each "epoch" (period between significant
events) we identify commits, map active doc sections, score risk, detect
silent gaps, model author collaboration, and emit EpochDelta trend data.

New in v3
─────────
• VelocityMetrics   — per-epoch commits/day + acceleration + momentum + stddev
• EpochRisk         — multi-factor risk scoring (churn, gaps, silos, sentiment)
• CrossReferenceMap — commit ↔ doc-section bi-directional links (confidence-weighted)
• TimelineGap       — silent-period detection between epochs
• AuthorNetwork     — collaboration graph (shared-file edges)
• EpochDelta        — consecutive-epoch diff (velocity Δ, theme drift, churn Δ)
• StoryEpoch        — extended with velocity, risk, cross_refs, delta
• SyncedTimeline    — extended with gaps, author_network, glossary passthrough
"""

from __future__ import annotations

import math
import re
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from itertools import combinations
from pathlib import Path
from typing import Optional

# ── Theme keywords ─────────────────────────────────────────────────────────────

THEME_KEYWORDS: dict[str, list[str]] = {
    "foundation":       ["initial", "bootstrap", "scaffold", "first commit", "setup", "init"],
    "architecture":     ["architecture", "modular", "monolith", "v2", "migration", "restructure", "refactor"],
    "auth":             ["auth", "jwt", "login", "token", "session", "oauth", "refresh", "keyring"],
    "database":         ["alembic", "migration", "schema", "postgres", "sqlite", "orm", "model"],
    "diagnostics":      ["diagnostic", "irt", "assessment", "item bank", "caps", "grade 4", "3pl"],
    "lessons":          ["lesson", "llm", "groq", "anthropic", "generation", "content"],
    "popia_compliance": ["popia", "consent", "gdpr", "privacy", "erasure", "audit", "compliance"],
    "ci_cd":            ["ci", "cd", "github actions", "workflow", "pipeline", "lint", "test", "pytest"],
    "observability":    ["prometheus", "grafana", "metrics", "alert", "monitoring", "loki", "slo"],
    "security":         ["security", "secret", "encrypt", "jwt secret", "ssl", "https", "pen test"],
    "frontend":         ["frontend", "next.js", "nextjs", "react", "typescript", "playwright", "e2e"],
    "infrastructure":   ["docker", "nginx", "redis", "azure", "kubernetes", "k8s", "bicep", "aca"],
    "production_ready": ["production", "readiness", "staging", "release", "beta", "go/no-go"],
    "bugfix":           ["fix", "bug", "patch", "repair", "correct", "broken", "resolve"],
    "documentation":    ["docs", "readme", "changelog", "todo", "roadmap", "documentation"],
}

_RISK_THEMES = {"security", "popia_compliance", "bugfix", "infrastructure"}
_MOMENTUM_THEMES = {"architecture", "ci_cd", "observability", "production_ready"}


def _detect_themes(text: str) -> list[str]:
    text_lower = text.lower()
    return [
        theme
        for theme, keywords in THEME_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]


def _parse_iso(date_str: str) -> Optional[datetime]:
    if not date_str or date_str == "unknown":
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str[:25], fmt[: len(date_str[:25])])
            except ValueError:
                continue
    return None


# ── Epoch detection ────────────────────────────────────────────────────────────

EPOCH_MARKERS: list[tuple[str, str]] = [
    (r"initial commit|bootstrap|scaffold|first commit",             "Foundation"),
    (r"v0\\.1\\.0|0\\.1\\.0.beta|first.beta",                           "Beta v0.1.0"),
    (r"v0\\.2\\.0|0\\.2\\.0.rc",                                        "Release Candidate v0.2.0"),
    (r"v2.*architect|complete.*v2.*migrat|breaking.*v2",            "V2 Architecture Migration"),
    (r"caps.*grade.4|grade.4.*item.bank|item.bank.*phase",          "CAPS Grade 4 Item Bank"),
    (r"production.readiness|codex.production|prod.ready",           "Production Readiness"),
    (r"pr.integration|merge.*production|release.*bundle",           "PR Integration & Release Prep"),
]


# ── v3 Analytics structs ───────────────────────────────────────────────────────

@dataclass
class VelocityMetrics:
    """Per-epoch commit velocity with trend signals."""
    commits_per_day: float      = 0.0
    span_days: int              = 0
    stddev: float               = 0.0          # stddev of daily commit counts
    acceleration: float         = 0.0          # Δ commits/day vs previous epoch
    momentum: float             = 0.0          # EMA-smoothed weekly commit rate
    percentile_rank: float      = 0.0          # 0–1; set after all epochs computed

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EpochRisk:
    """Multi-factor risk score for an epoch (0–100, higher = riskier)."""
    score: float                = 0.0
    level: str                  = "low"        # low / medium / high / critical
    churn_factor: float         = 0.0
    gap_factor: float           = 0.0
    silo_factor: float          = 0.0
    sentiment_factor: float     = 0.0
    breaking_factor: float      = 0.0
    risk_themes: list[str]      = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CrossRef:
    """A single commit ↔ doc-section link."""
    commit_hash: str
    commit_subject: str
    doc_path: str
    doc_section: str
    confidence: float           # 0–1 keyword overlap score

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CrossReferenceMap:
    """Bi-directional commit ↔ doc-section index for a timeline."""
    entries: list[CrossRef] = field(default_factory=list)

    # Convenience look-ups (populated by build_synced_timeline)
    commits_to_docs: dict[str, list[str]] = field(default_factory=dict)
    docs_to_commits: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "commits_to_docs": self.commits_to_docs,
            "docs_to_commits": self.docs_to_commits,
        }


@dataclass
class TimelineGap:
    """A silent period between two epochs (no commits)."""
    before_epoch: str
    after_epoch: str
    gap_start: str
    gap_end: str
    gap_days: int
    severity: str               # minor (<7d) / notable (7–30d) / major (>30d)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuthorEdge:
    """Collaboration edge: two authors who touched the same files."""
    author_a: str
    author_b: str
    shared_files: int
    shared_commit_epochs: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuthorNetwork:
    """Collaboration graph derived from file co-authorship."""
    nodes: list[dict]           = field(default_factory=list)
    edges: list[AuthorEdge]     = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "edges": [e.to_dict() for e in self.edges],
        }


@dataclass
class EpochDelta:
    """Trend diff between two consecutive epochs."""
    from_epoch: str
    to_epoch: str
    velocity_change: float      # commits/day Δ
    theme_gained: list[str]
    theme_lost: list[str]
    churn_change: int           # (ins+dels) Δ
    risk_change: float          # EpochRisk.score Δ
    commit_count_change: int

    def to_dict(self) -> dict:
        return asdict(self)


# ── Core domain structs ────────────────────────────────────────────────────────

@dataclass
class CommitSummary:
    hash: str
    short: str
    date: str
    author: str
    subject: str
    themes: list[str]
    files_changed: list[str]
    stats: dict
    pr_number: Optional[str]
    is_merge: bool
    cc_type: Optional[str] = None
    cc_breaking: bool = False


@dataclass
class StoryEpoch:
    name: str
    start_date: str
    end_date: str
    commit_count: int
    commits: list[CommitSummary]
    dominant_themes: list[str]
    key_files_touched: list[str]
    docs_active: list[str]
    summary_hint: str
    total_insertions: int           = 0
    total_deletions: int            = 0
    velocity: VelocityMetrics       = field(default_factory=VelocityMetrics)     # v3
    risk: EpochRisk                 = field(default_factory=EpochRisk)            # v3
    cross_refs: list[CrossRef]      = field(default_factory=list)                 # v3
    breaking_changes: int           = 0                                            # v3
    unique_authors: list[str]       = field(default_factory=list)                 # v3

    def to_dict(self) -> dict:
        d = asdict(self)
        d["velocity"]    = self.velocity.to_dict()
        d["risk"]        = self.risk.to_dict()
        d["cross_refs"]  = [r.to_dict() for r in self.cross_refs]
        return d


@dataclass
class SyncedTimeline:
    repo: str
    generated_at: str
    total_commits: int
    total_docs: int
    epochs: list[StoryEpoch]
    doc_index: list[dict]
    raw_commits: list[dict]
    gaps: list[TimelineGap]             = field(default_factory=list)             # v3
    author_network: AuthorNetwork       = field(default_factory=AuthorNetwork)    # v3
    cross_reference_map: CrossReferenceMap = field(default_factory=CrossReferenceMap)  # v3
    epoch_deltas: list[EpochDelta]      = field(default_factory=list)             # v3

    def to_dict(self) -> dict:
        return {
            "repo":                self.repo,
            "generated_at":        self.generated_at,
            "total_commits":       self.total_commits,
            "total_docs":          self.total_docs,
            "epochs":              [e.to_dict() for e in self.epochs],
            "doc_index":           self.doc_index,
            "raw_commits":         self.raw_commits,
            "gaps":                [g.to_dict() for g in self.gaps],
            "author_network":      self.author_network.to_dict(),
            "cross_reference_map": self.cross_reference_map.to_dict(),
            "epoch_deltas":        [d.to_dict() for d in self.epoch_deltas],
        }


# ── v3 Analytics functions ─────────────────────────────────────────────────────

def _compute_epoch_velocity(commits: list[CommitSummary]) -> VelocityMetrics:
    dates = [_parse_iso(c.date) for c in commits]
    dates = [d for d in dates if d]
    if not dates:
        return VelocityMetrics()

    first, last = min(dates), max(dates)
    span_days = max((last - first).days, 1)
    cpd = round(len(dates) / span_days, 4)

    # Daily bucket counts
    day_map: dict[str, int] = defaultdict(int)
    for d in dates:
        day_map[d.strftime("%Y-%m-%d")] += 1
    daily_vals = list(day_map.values())

    mean = sum(daily_vals) / len(daily_vals)
    variance = sum((x - mean) ** 2 for x in daily_vals) / max(len(daily_vals), 1)
    stddev = round(math.sqrt(variance), 3)

    # Momentum: EMA over sorted daily vals (α=0.35)
    alpha = 0.35
    ema = daily_vals[0] if daily_vals else 0.0
    for v in daily_vals[1:]:
        ema = alpha * v + (1 - alpha) * ema
    momentum = round(ema, 3)

    return VelocityMetrics(
        commits_per_day=cpd,
        span_days=span_days,
        stddev=stddev,
        momentum=momentum,
    )


def _compute_epoch_risk(
    epoch: StoryEpoch,
    doc_sentiments: dict[str, dict],
    all_authors_file_map: dict[str, set[str]],
) -> EpochRisk:
    """
    Multi-factor risk score.
    - churn_factor    (0–30): high ins+dels relative to commit count
    - gap_factor      (0–20): epoch span with few commits (sparse activity)
    - silo_factor     (0–20): single-author files in key_files
    - sentiment_factor(0–15): risk keyword density in active docs
    - breaking_factor (0–15): breaking changes in epoch
    """
    churn = epoch.total_insertions + epoch.total_deletions
    churn_per_commit = churn / max(epoch.commit_count, 1)
    churn_factor = min(30.0, round(churn_per_commit / 200 * 30, 1))

    span = epoch.velocity.span_days
    if span > 0 and epoch.commit_count > 0:
        gap_ratio = 1.0 - min(epoch.velocity.commits_per_day / 2.0, 1.0)
        gap_factor = round(gap_ratio * 20, 1)
    else:
        gap_factor = 10.0

    # Silo: files touched only by one author
    silo_count = sum(
        1 for f in epoch.key_files_touched
        if len(all_authors_file_map.get(f, set())) <= 1
    )
    silo_factor = min(20.0, round(silo_count / max(len(epoch.key_files_touched), 1) * 20, 1))

    # Sentiment from active docs
    risk_densities = [
        doc_sentiments.get(d, {}).get("risk", 0.0)
        for d in epoch.docs_active
    ]
    avg_risk = sum(risk_densities) / max(len(risk_densities), 1)
    sentiment_factor = round(avg_risk * 150, 1)  # 0-15 range (risk density is small)
    sentiment_factor = min(15.0, sentiment_factor)

    breaking_factor = min(15.0, epoch.breaking_changes * 5.0)

    risk_theme_hits = [t for t in epoch.dominant_themes if t in _RISK_THEMES]
    score = round(churn_factor + gap_factor + silo_factor + sentiment_factor + breaking_factor, 1)

    if score >= 70:
        level = "critical"
    elif score >= 45:
        level = "high"
    elif score >= 25:
        level = "medium"
    else:
        level = "low"

    return EpochRisk(
        score=score,
        level=level,
        churn_factor=churn_factor,
        gap_factor=gap_factor,
        silo_factor=silo_factor,
        sentiment_factor=sentiment_factor,
        breaking_factor=breaking_factor,
        risk_themes=risk_theme_hits,
    )


def _build_cross_reference_map(
    epochs: list[StoryEpoch],
    docs_data: list[dict],
) -> CrossReferenceMap:
    """
    For each commit, score its affinity to each doc section by keyword overlap.
    Emits CrossRef entries with confidence ≥ 0.15.
    """
    # Pre-index: doc sections keyed by (doc_path, heading)
    sections_index: list[tuple[str, str, set[str]]] = []
    for doc in docs_data:
        for sec in doc.get("sections", []):
            heading = sec.get("heading", "")
            content = sec.get("content", "")
            kws = set(re.findall(r"\b\w{4,}\b", f"{heading} {content}".lower()))
            sections_index.append((doc["path"], heading, kws))

    entries: list[CrossRef] = []
    commit_to_docs: dict[str, list[str]] = defaultdict(list)
    doc_to_commits: dict[str, list[str]] = defaultdict(list)

    for epoch in epochs:
        for c in epoch.commits:
            commit_kws = set(
                re.findall(r"\b\w{4,}\b", f"{c.subject} {' '.join(c.files_changed)}".lower())
            )
            if not commit_kws:
                continue
            for doc_path, sec_heading, sec_kws in sections_index:
                overlap = commit_kws & sec_kws
                if not overlap:
                    continue
                confidence = round(len(overlap) / math.sqrt(len(commit_kws) * max(len(sec_kws), 1)), 4)
                if confidence < 0.15:
                    continue
                entries.append(CrossRef(
                    commit_hash=c.hash,
                    commit_subject=c.subject,
                    doc_path=doc_path,
                    doc_section=sec_heading,
                    confidence=confidence,
                ))
                commit_to_docs[c.hash].append(f"{doc_path}#{sec_heading}")
                doc_to_commits[f"{doc_path}#{sec_heading}"].append(c.hash)

    # Inject per-epoch cross_refs
    by_hash = defaultdict(list)
    for e in entries:
        by_hash[e.commit_hash].append(e)
    for epoch in epochs:
        epoch.cross_refs = [
            ref for c in epoch.commits
            for ref in by_hash.get(c.hash, [])
        ]

    return CrossReferenceMap(
        entries=entries,
        commits_to_docs=dict(commit_to_docs),
        docs_to_commits=dict(doc_to_commits),
    )


def _detect_timeline_gaps(epochs: list[StoryEpoch]) -> list[TimelineGap]:
    gaps: list[TimelineGap] = []
    for i in range(1, len(epochs)):
        prev, curr = epochs[i - 1], epochs[i]
        prev_end  = _parse_iso(prev.end_date)
        curr_start = _parse_iso(curr.start_date)
        if not (prev_end and curr_start):
            continue
        gap_days = (curr_start - prev_end).days
        if gap_days < 2:
            continue
        severity = "major" if gap_days > 30 else ("notable" if gap_days >= 7 else "minor")
        gaps.append(TimelineGap(
            before_epoch=prev.name,
            after_epoch=curr.name,
            gap_start=prev_end.date().isoformat(),
            gap_end=curr_start.date().isoformat(),
            gap_days=gap_days,
            severity=severity,
        ))
    return gaps


def _build_author_network(epochs: list[StoryEpoch]) -> AuthorNetwork:
    """Build a collaboration graph from shared-file authorship within epochs."""
    # author → files touched (epoch-scoped for edge labelling)
    author_files: dict[str, set[str]] = defaultdict(set)
    author_epochs: dict[str, set[str]] = defaultdict(set)
    commit_counts: dict[str, int] = defaultdict(int)

    for epoch in epochs:
        for c in epoch.commits:
            author_files[c.author].update(c.files_changed)
            author_epochs[c.author].add(epoch.name)
            commit_counts[c.author] += 1

    authors = list(author_files.keys())
    nodes = [
        {
            "id": a,
            "commit_count": commit_counts[a],
            "epoch_count": len(author_epochs[a]),
            "file_count": len(author_files[a]),
        }
        for a in authors
    ]

    edges: list[AuthorEdge] = []
    for a, b in combinations(sorted(authors), 2):
        shared = author_files[a] & author_files[b]
        if not shared:
            continue
        shared_epochs = list(author_epochs[a] & author_epochs[b])
        edges.append(AuthorEdge(
            author_a=a,
            author_b=b,
            shared_files=len(shared),
            shared_commit_epochs=shared_epochs,
        ))

    edges.sort(key=lambda e: e.shared_files, reverse=True)
    return AuthorNetwork(nodes=nodes, edges=edges[:100])


def _build_epoch_deltas(epochs: list[StoryEpoch]) -> list[EpochDelta]:
    deltas: list[EpochDelta] = []
    for i in range(1, len(epochs)):
        prev, curr = epochs[i - 1], epochs[i]
        deltas.append(EpochDelta(
            from_epoch=prev.name,
            to_epoch=curr.name,
            velocity_change=round(curr.velocity.commits_per_day - prev.velocity.commits_per_day, 4),
            theme_gained=[t for t in curr.dominant_themes if t not in prev.dominant_themes],
            theme_lost=[t for t in prev.dominant_themes if t not in curr.dominant_themes],
            churn_change=(
                (curr.total_insertions + curr.total_deletions)
                - (prev.total_insertions + prev.total_deletions)
            ),
            risk_change=round(curr.risk.score - prev.risk.score, 1),
            commit_count_change=curr.commit_count - prev.commit_count,
        ))
    return deltas


def _assign_velocity_percentiles(epochs: list[StoryEpoch]) -> None:
    cpds = [e.velocity.commits_per_day for e in epochs]
    if not cpds:
        return
    sorted_cpds = sorted(cpds)
    for epoch in epochs:
        rank = sorted_cpds.index(epoch.velocity.commits_per_day)
        epoch.velocity.percentile_rank = round(rank / max(len(sorted_cpds) - 1, 1), 4)


# ── Main sync function ─────────────────────────────────────────────────────────

def build_synced_timeline(
    commits_data: list[dict],
    docs_data: list[dict],
    repo_name: str = "EduBoost_V2",
) -> SyncedTimeline:
    """
    Build a SyncedTimeline from raw commit dicts and doc dicts.

    v3 additions: per-epoch velocity, risk scoring, cross-reference map,
    gap detection, author network, and epoch-to-epoch delta analysis.
    """

    # ── Annotate commits ──────────────────────────────────────────────────────
    annotated: list[CommitSummary] = []
    for c in commits_data:
        search_text = (
            f"{c.get('subject', '')} {c.get('body', '')} "
            f"{' '.join(c.get('files_changed', []))}"
        )
        annotated.append(CommitSummary(
            hash=c["hash"],
            short=c["short"],
            date=c["date"],
            author=c["author"],
            subject=c["subject"],
            themes=_detect_themes(search_text),
            files_changed=c.get("files_changed", []),
            stats=c.get("stats", {}),
            pr_number=c.get("pr_number"),
            is_merge=c.get("is_merge", False),
            cc_type=c.get("cc_type"),
            cc_breaking=c.get("cc_breaking", False),
        ))

    # ── Doc index + sentiment cache ───────────────────────────────────────────
    doc_index = [
        {"path": d["path"], "doc_type": d["doc_type"], "title": d["title"], "metadata": d["metadata"]}
        for d in docs_data
    ]
    doc_sentiments: dict[str, dict] = {
        d["path"]: d.get("sentiment", {})
        for d in docs_data
    }

    # ── Assign commits to epochs ──────────────────────────────────────────────
    epochs_map: dict[str, list[CommitSummary]] = {}
    current_epoch = "Foundation"

    for commit in annotated:
        subj = commit.subject.lower()
        for pattern, epoch_name in EPOCH_MARKERS:
            if re.search(pattern, subj, re.IGNORECASE):
                current_epoch = epoch_name
                break
        epochs_map.setdefault(current_epoch, []).append(commit)

    # ── Build per-file author map (for silo scoring) ──────────────────────────
    file_author_map: dict[str, set[str]] = defaultdict(set)
    for c in annotated:
        for f in c.files_changed:
            file_author_map[f].add(c.author)

    # ── Build StoryEpoch objects ──────────────────────────────────────────────
    story_epochs: list[StoryEpoch] = []

    for epoch_name, epoch_commits in epochs_map.items():
        if not epoch_commits:
            continue

        dates = [_parse_iso(c.date) for c in epoch_commits]
        dates = [d for d in dates if d]
        start = min(dates).strftime("%Y-%m-%d") if dates else "unknown"
        end   = max(dates).strftime("%Y-%m-%d") if dates else "unknown"

        all_themes:  list[str] = []
        all_files:   list[str] = []
        total_ins = total_dels = breaking = 0
        authors: set[str] = set()

        for c in epoch_commits:
            all_themes.extend(c.themes)
            all_files.extend(c.files_changed)
            total_ins  += c.stats.get("insertions", 0)
            total_dels += c.stats.get("deletions", 0)
            authors.add(c.author)
            if c.cc_breaking:
                breaking += 1

        theme_counts = Counter(all_themes)
        file_counts  = Counter(all_files)
        dominant_themes = [t for t, _ in theme_counts.most_common(5)]
        key_files = [f for f, _ in file_counts.most_common(10)]

        def _doc_relevant(doc: dict) -> bool:
            doc_text = f"{doc['title']} {doc['doc_type']} {doc['path']}".lower()
            return any(
                kw in doc_text
                for theme in dominant_themes
                for kw in THEME_KEYWORDS.get(theme, [])
            )

        relevant_docs = [d["title"] for d in doc_index if _doc_relevant(d)]
        if not relevant_docs:
            relevant_docs = [d["title"] for d in doc_index[:3]]

        hint_parts = []
        if total_ins or total_dels:
            hint_parts.append(f"+{total_ins}/-{total_dels} lines")
        if dominant_themes:
            hint_parts.append(f"themes: {', '.join(dominant_themes[:3])}")
        hint = "; ".join(hint_parts) if hint_parts else "general development work"

        velocity = _compute_epoch_velocity(epoch_commits)

        epoch = StoryEpoch(
            name=epoch_name,
            start_date=start,
            end_date=end,
            commit_count=len(epoch_commits),
            commits=epoch_commits,
            dominant_themes=dominant_themes,
            key_files_touched=key_files,
            docs_active=list(dict.fromkeys(relevant_docs))[:6],
            summary_hint=hint,
            total_insertions=total_ins,
            total_deletions=total_dels,
            velocity=velocity,
            breaking_changes=breaking,
            unique_authors=sorted(authors),
        )
        story_epochs.append(epoch)

    # ── Risk scoring (needs all epochs for context) ───────────────────────────
    for epoch in story_epochs:
        epoch.risk = _compute_epoch_risk(epoch, doc_sentiments, dict(file_author_map))

    # ── Velocity acceleration (Δ vs previous epoch) ───────────────────────────
    for i in range(1, len(story_epochs)):
        prev_cpd = story_epochs[i - 1].velocity.commits_per_day
        curr_cpd = story_epochs[i].velocity.commits_per_day
        story_epochs[i].velocity.acceleration = round(curr_cpd - prev_cpd, 4)

    _assign_velocity_percentiles(story_epochs)

    # ── Cross-reference map ───────────────────────────────────────────────────
    xref_map = _build_cross_reference_map(story_epochs, docs_data)

    # ── Timeline gaps ─────────────────────────────────────────────────────────
    gaps = _detect_timeline_gaps(story_epochs)

    # ── Author network ────────────────────────────────────────────────────────
    author_network = _build_author_network(story_epochs)

    # ── Epoch deltas ──────────────────────────────────────────────────────────
    epoch_deltas = _build_epoch_deltas(story_epochs)

    total_xrefs = len(xref_map.entries)
    total_gaps  = len(gaps)
    total_edges = len(author_network.edges)
    print(
        f"[sync_engine] ✓ {len(story_epochs)} epochs · "
        f"{total_xrefs} cross-refs · "
        f"{total_gaps} gap(s) · "
        f"{total_edges} author edge(s)"
    )

    return SyncedTimeline(
        repo=repo_name,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_commits=len(annotated),
        total_docs=len(docs_data),
        epochs=story_epochs,
        doc_index=doc_index,
        raw_commits=[c.__dict__ for c in annotated],
        gaps=gaps,
        author_network=author_network,
        cross_reference_map=xref_map,
        epoch_deltas=epoch_deltas,
    )


def save_timeline_json(timeline: SyncedTimeline, output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(timeline.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"[sync_engine] Saved timeline ({len(timeline.epochs)} epochs) → {output_path}")


def load_timeline_json(input_path: Path) -> dict:
    with open(input_path, encoding="utf-8") as f:
        return json.load(f)
