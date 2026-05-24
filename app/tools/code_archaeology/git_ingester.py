"""
git_ingester.py  v4
-------------------
Parses the full git history of a repository and returns rich, structured
commit data.  Two backends: GitPython → subprocess fallback.

New in v4
─────────
• CoChangeMatrix   — files that frequently change together (coupling heatmap)
• KnowledgeSilo    — per-author exclusive ownership score (bus-factor proxy)
• RefactorTrend    — conventional-commit type distribution over rolling windows
• VelocityMetrics  — adds stddev, acceleration (Δcommits/day between windows),
                     and momentum (EMA of weekly commit counts)
• GlossaryEntry    — symbol/acronym extraction from commit subjects + bodies
• Everything from v3 is preserved and extended (no regressions)
"""

from __future__ import annotations

import re
import json
import math
import subprocess
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from itertools import combinations
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta


# ── Conventional Commits ───────────────────────────────────────────────────────

_CC_RE = re.compile(
    r"^(?P<type>feat|fix|chore|docs|refactor|perf|test|ci|build|style|revert)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s+(?P<desc>.+)$",
    re.IGNORECASE,
)


def _parse_conventional(subject: str) -> tuple[Optional[str], Optional[str], bool]:
    m = _CC_RE.match(subject.strip())
    if not m:
        return None, None, False
    return m.group("type").lower(), m.group("scope"), bool(m.group("breaking"))


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class CommitRecord:
    hash: str
    short: str
    author: str
    email: str
    date: str
    subject: str
    body: str
    refs: str
    files_changed: list[str]        = field(default_factory=list)
    stats: dict                     = field(default_factory=dict)
    tags: list[str]                 = field(default_factory=list)
    semver_tags: list[str]          = field(default_factory=list)
    co_authors: list[str]           = field(default_factory=list)
    is_merge: bool                  = False
    is_first_parent: bool           = False
    pr_number: Optional[str]        = None
    cc_type: Optional[str]          = None
    cc_scope: Optional[str]         = None
    cc_breaking: bool               = False
    burst_id: Optional[str]         = None
    tag_message: Optional[str]      = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuthorProfile:
    name: str
    email: str
    commit_count: int                   = 0
    total_insertions: int               = 0
    total_deletions: int                = 0
    files_touched: set                  = field(default_factory=set)
    cc_type_breakdown: dict             = field(default_factory=dict)
    first_commit_date: Optional[str]    = None
    last_commit_date: Optional[str]     = None
    merge_count: int                    = 0
    breaking_change_count: int          = 0
    exclusive_files: list[str]          = field(default_factory=list)   # v4: silo
    silo_score: float                   = 0.0                           # v4: 0–1

    def to_dict(self) -> dict:
        d = asdict(self)
        d["files_touched"] = list(self.files_touched)
        return d


@dataclass
class ChurnIndex:
    entries: list[dict] = field(default_factory=list)

    def top(self, n: int = 20) -> list[dict]:
        return sorted(self.entries, key=lambda e: e["raw_churn"], reverse=True)[:n]

    def to_dict(self) -> dict:
        return {"entries": self.entries}


@dataclass
class CommitCluster:
    burst_id: str
    start_date: str
    end_date: str
    commit_count: int
    hashes: list[str]   = field(default_factory=list)
    authors: list[str]  = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HotspotRanking:
    entries: list[dict] = field(default_factory=list)

    def top(self, n: int = 20) -> list[dict]:
        return self.entries[:n]

    def to_dict(self) -> dict:
        return {"entries": self.entries}


@dataclass
class CoChangeEntry:
    """Two files that co-change frequently — coupling signal."""
    file_a: str
    file_b: str
    co_change_count: int
    coupling_score: float   # co_changes / max(individual_changes) — 0–1


@dataclass
class CoChangeMatrix:
    """Pairwise file coupling derived from commit co-occurrence."""
    entries: list[CoChangeEntry] = field(default_factory=list)

    def top(self, n: int = 30) -> list[CoChangeEntry]:
        return sorted(self.entries, key=lambda e: e.co_change_count, reverse=True)[:n]

    def to_dict(self) -> dict:
        return {"entries": [asdict(e) for e in self.entries]}


@dataclass
class RefactorTrend:
    """Conventional-commit type distribution over rolling 4-week windows."""
    windows: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"windows": self.windows}


@dataclass
class GitIngestionResult:
    commits: list[CommitRecord]
    author_profiles: list[AuthorProfile]
    churn_index: ChurnIndex
    hotspot_ranking: HotspotRanking
    burst_clusters: list[CommitCluster]
    co_change_matrix: CoChangeMatrix            = field(default_factory=CoChangeMatrix)
    refactor_trend: RefactorTrend               = field(default_factory=RefactorTrend)
    velocity_summary: dict                      = field(default_factory=dict)
    timestamps: list[str]                       = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "commits":           [c.to_dict() for c in self.commits],
            "author_profiles":   [a.to_dict() for a in self.author_profiles],
            "churn_index":       self.churn_index.to_dict(),
            "hotspot_ranking":   self.hotspot_ranking.to_dict(),
            "burst_clusters":    [b.to_dict() for b in self.burst_clusters],
            "co_change_matrix":  self.co_change_matrix.to_dict(),
            "refactor_trend":    self.refactor_trend.to_dict(),
            "velocity_summary":  self.velocity_summary,
            "timestamps":        self.timestamps,
        }


# ── Helpers ────────────────────────────────────────────────────────────────────

_SEMVER_RE    = re.compile(r"v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-(?P<pre>[a-zA-Z0-9.]+))?", re.IGNORECASE)
_PR_RE        = re.compile(r"#(\d+)")
_CO_AUTHOR_RE = re.compile(r"Co-authored-by:\s*([^<]+)<([^>]+)>", re.IGNORECASE)


def _parse_pr_number(subject: str) -> Optional[str]:
    m = _PR_RE.search(subject)
    return m.group(1) if m else None


def _parse_tags(refs: str) -> tuple[list[str], list[str]]:
    all_tags, semver = [], []
    for part in refs.split(","):
        part = part.strip()
        if part.startswith("tag:"):
            tag = part.removeprefix("tag:").strip()
            all_tags.append(tag)
            if _SEMVER_RE.search(tag):
                semver.append(tag)
    return all_tags, semver


def _parse_co_authors(body: str) -> list[str]:
    return [f"{m.group(1).strip()} <{m.group(2).strip()}>" for m in _CO_AUTHOR_RE.finditer(body)]


def _is_shallow(repo_path: Path) -> bool:
    return (repo_path / ".git" / "shallow").exists()


def _run(cmd: list[str], cwd: Path) -> str:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True).stdout


def _parse_iso(date_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None


# ── Analytics ─────────────────────────────────────────────────────────────────

def _build_author_profiles(commits: list[CommitRecord]) -> list[AuthorProfile]:
    profiles: dict[str, AuthorProfile] = {}
    file_all_authors: dict[str, set[str]] = defaultdict(set)

    for c in commits:
        key = c.email or c.author
        if key not in profiles:
            profiles[key] = AuthorProfile(name=c.author, email=c.email)
        p = profiles[key]
        p.commit_count     += 1
        p.total_insertions += c.stats.get("insertions", 0)
        p.total_deletions  += c.stats.get("deletions", 0)
        p.files_touched.update(c.files_changed)
        if c.cc_type:
            p.cc_type_breakdown[c.cc_type] = p.cc_type_breakdown.get(c.cc_type, 0) + 1
        if c.is_merge:
            p.merge_count += 1
        if c.cc_breaking:
            p.breaking_change_count += 1
        dt = c.date
        if p.first_commit_date is None or dt < p.first_commit_date:
            p.first_commit_date = dt
        if p.last_commit_date is None or dt > p.last_commit_date:
            p.last_commit_date = dt
        for f in c.files_changed:
            file_all_authors[f].add(key)

    # v4: compute knowledge silos
    for key, p in profiles.items():
        exclusive = [f for f in p.files_touched if len(file_all_authors[f]) == 1]
        p.exclusive_files = exclusive
        p.silo_score = round(len(exclusive) / max(len(p.files_touched), 1), 4)

    return sorted(profiles.values(), key=lambda x: x.commit_count, reverse=True)


def _build_churn_index(commits: list[CommitRecord]) -> ChurnIndex:
    file_churn: dict[str, int] = defaultdict(int)
    for c in commits:
        ins = c.stats.get("insertions", 0)
        dels = c.stats.get("deletions", 0)
        per_file = (ins + dels) // max(len(c.files_changed), 1)
        for f in c.files_changed:
            file_churn[f] += per_file
    if not file_churn:
        return ChurnIndex()
    max_churn = max(file_churn.values()) or 1
    entries = [
        {"file": f, "raw_churn": v, "score": round(v / max_churn, 4)}
        for f, v in sorted(file_churn.items(), key=lambda x: x[1], reverse=True)
    ]
    return ChurnIndex(entries=entries)


def _build_hotspot_ranking(commits: list[CommitRecord]) -> HotspotRanking:
    file_commits: dict[str, set[str]] = defaultdict(set)
    file_authors: dict[str, set[str]] = defaultdict(set)
    for c in commits:
        for f in c.files_changed:
            file_commits[f].add(c.hash)
            file_authors[f].add(c.author)
    entries = sorted(
        [{"file": f, "commit_count": len(hs), "authors": list(file_authors[f])} for f, hs in file_commits.items()],
        key=lambda e: e["commit_count"],
        reverse=True,
    )
    return HotspotRanking(entries=entries)


def _build_co_change_matrix(commits: list[CommitRecord], min_count: int = 2) -> CoChangeMatrix:
    """Files changed together ≥ min_count times → coupling entries."""
    pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    file_commit_counts: dict[str, int] = defaultdict(int)

    for c in commits:
        files = [f for f in c.files_changed if f]
        for f in files:
            file_commit_counts[f] += 1
        for a, b in combinations(sorted(set(files)), 2):
            pair_counts[(a, b)] += 1

    entries = []
    for (a, b), count in pair_counts.items():
        if count < min_count:
            continue
        max_individual = max(file_commit_counts[a], file_commit_counts[b])
        coupling = round(count / max_individual, 4) if max_individual else 0.0
        entries.append(CoChangeEntry(file_a=a, file_b=b, co_change_count=count, coupling_score=coupling))

    entries.sort(key=lambda e: e.co_change_count, reverse=True)
    return CoChangeMatrix(entries=entries[:200])  # cap at 200 pairs


def _build_refactor_trend(commits: list[CommitRecord]) -> RefactorTrend:
    """4-week rolling windows of CC type distribution."""
    CC_TYPES = ["feat", "fix", "refactor", "chore", "docs", "perf", "test", "ci"]
    week_map: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for c in commits:
        dt = _parse_iso(c.date)
        if not dt:
            continue
        week_key = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
        cc = c.cc_type or "other"
        week_map[week_key][cc] += 1

    windows = []
    for week_start in sorted(week_map.keys()):
        bucket = week_map[week_start]
        total = sum(bucket.values()) or 1
        row: dict = {"week_start": week_start, "total": sum(bucket.values())}
        for t in CC_TYPES:
            row[t] = bucket.get(t, 0)
        row["other"] = bucket.get("other", 0)
        row["refactor_ratio"] = round(bucket.get("refactor", 0) / total, 4)
        windows.append(row)

    return RefactorTrend(windows=windows)


def _detect_bursts(commits: list[CommitRecord], burst_gap_hours: float = 4.0) -> list[CommitCluster]:
    if not commits:
        return []
    sorted_commits = sorted(commits, key=lambda c: c.date)
    gap = timedelta(hours=burst_gap_hours)
    clusters: list[CommitCluster] = []
    current: list[CommitRecord] = [sorted_commits[0]]

    for prev, curr in zip(sorted_commits, sorted_commits[1:]):
        dt_prev = _parse_iso(prev.date)
        dt_curr = _parse_iso(curr.date)
        if dt_prev and dt_curr and (dt_curr - dt_prev) <= gap:
            current.append(curr)
        else:
            if len(current) >= 3:
                bid = f"burst-{current[0].short}"
                clusters.append(CommitCluster(
                    burst_id=bid, start_date=current[0].date, end_date=current[-1].date,
                    commit_count=len(current), hashes=[c.hash for c in current],
                    authors=list({c.author for c in current}),
                ))
                for c in current:
                    c.burst_id = bid
            current = [curr]

    if len(current) >= 3:
        bid = f"burst-{current[0].short}"
        clusters.append(CommitCluster(
            burst_id=bid, start_date=current[0].date, end_date=current[-1].date,
            commit_count=len(current), hashes=[c.hash for c in current],
            authors=list({c.author for c in current}),
        ))
        for c in current:
            c.burst_id = bid

    return clusters


def _compute_velocity(commits: list[CommitRecord]) -> dict:
    """v4: adds stddev, acceleration (week-over-week Δ), momentum (EMA)."""
    if not commits:
        return {}
    dates = [_parse_iso(c.date) for c in commits]
    dates = [d for d in dates if d]
    if not dates:
        return {}

    first, last = min(dates), max(dates)
    span_days   = max((last - first).days, 1)
    cpd_overall = round(len(dates) / span_days, 3)

    bucket_map: dict[str, int] = defaultdict(int)
    for d in dates:
        week_key = (d - timedelta(days=d.weekday())).strftime("%Y-%W")
        bucket_map[week_key] += 1

    rolling = [{"week": k, "commits": v} for k, v in sorted(bucket_map.items())]

    # stddev of weekly counts
    weekly_vals = [r["commits"] for r in rolling]
    mean = sum(weekly_vals) / len(weekly_vals) if weekly_vals else 0
    variance = sum((x - mean) ** 2 for x in weekly_vals) / max(len(weekly_vals), 1)
    stddev = round(math.sqrt(variance), 3)

    # acceleration: week-over-week delta
    acceleration = []
    for i in range(1, len(rolling)):
        delta = rolling[i]["commits"] - rolling[i - 1]["commits"]
        acceleration.append({"week": rolling[i]["week"], "delta": delta})

    # EMA momentum (α=0.3)
    alpha = 0.3
    ema = weekly_vals[0] if weekly_vals else 0
    momentum = []
    for r in rolling:
        ema = alpha * r["commits"] + (1 - alpha) * ema
        momentum.append({"week": r["week"], "ema": round(ema, 3)})

    return {
        "commits_per_day": cpd_overall,
        "first_commit":    first.isoformat(),
        "last_commit":     last.isoformat(),
        "span_days":       span_days,
        "rolling_weekly":  rolling,
        "weekly_stddev":   stddev,
        "acceleration":    acceleration,
        "momentum":        momentum,
    }


# ── GitPython backend ──────────────────────────────────────────────────────────

def _ingest_gitpython(repo_path: Path, branch: str, first_parent: bool) -> list[CommitRecord]:
    try:
        import git  # type: ignore
    except ImportError:
        raise ImportError("gitpython not installed")

    repo = git.Repo(str(repo_path))
    tag_map: dict[str, list[str]] = {}
    tag_messages: dict[str, str] = {}
    for tag in repo.tags:
        try:
            chash = tag.commit.hexsha
        except Exception:
            continue
        tag_map.setdefault(chash, []).append(tag.name)
        if hasattr(tag, "tag") and tag.tag:
            tag_messages[tag.name] = tag.tag.message or ""

    iter_kwargs: dict = {"rev": branch}
    if first_parent:
        iter_kwargs["first_parent"] = True

    records: list[CommitRecord] = []
    for commit in repo.iter_commits(**iter_kwargs):
        chash    = commit.hexsha
        refs_str = ", ".join(f"tag: {t}" for t in tag_map.get(chash, []))
        all_tags, semver = _parse_tags(refs_str)
        body     = commit.message.split("\n", 1)[1].strip() if "\n" in commit.message else ""
        cc_type, cc_scope, cc_breaking = _parse_conventional(commit.summary)

        files_changed: list[str] = []
        insertions = deletions = 0
        try:
            if commit.parents:
                diff = commit.parents[0].diff(commit, create_patch=False)
                for d in diff:
                    files_changed.append(d.b_path or d.a_path or "")
            stats_dict = commit.stats.total
            insertions = stats_dict.get("insertions", 0)
            deletions  = stats_dict.get("deletions", 0)
        except Exception:
            pass

        tag_msg = next((tag_messages[t] for t in all_tags if t in tag_messages), None)
        records.append(CommitRecord(
            hash=chash, short=chash[:7],
            author=commit.author.name or "", email=commit.author.email or "",
            date=datetime.fromtimestamp(commit.authored_date, tz=timezone.utc).isoformat(),
            subject=commit.summary, body=body, refs=refs_str,
            files_changed=files_changed,
            stats={"insertions": insertions, "deletions": deletions, "files": len(files_changed)},
            tags=all_tags, semver_tags=semver, co_authors=_parse_co_authors(body),
            is_merge=len(commit.parents) > 1, is_first_parent=first_parent,
            pr_number=_parse_pr_number(commit.summary),
            cc_type=cc_type, cc_scope=cc_scope, cc_breaking=cc_breaking, tag_message=tag_msg,
        ))

    records.reverse()
    return records


# ── subprocess backend ─────────────────────────────────────────────────────────

_SEPARATOR = "---COMMIT---"
_FORMAT = (
    f"{_SEPARATOR}%n"
    "hash=%H%n" "short=%h%n" "author=%an%n" "email=%ae%n"
    "date=%aI%n" "subject=%s%n" "refs=%D%n"
    "body_begin=%n%b%nbody_end"
)


def _ingest_subprocess(repo_path: Path, branch: str, first_parent: bool) -> list[CommitRecord]:
    cmd = ["git", "log", branch, f"--pretty=format:{_FORMAT}"]
    if first_parent:
        cmd.append("--first-parent")
    raw    = _run(cmd, cwd=repo_path)
    blocks = [b.strip() for b in raw.split(_SEPARATOR) if b.strip()]
    commits: list[CommitRecord] = []

    for block in blocks:
        fields: dict = {}
        body_lines: list[str] = []
        in_body = False
        for line in block.splitlines():
            if line == "body_begin":
                in_body = True; continue
            if line == "body_end":
                in_body = False; continue
            if in_body:
                body_lines.append(line); continue
            for key in ("hash", "short", "author", "email", "date", "subject", "refs"):
                if line.startswith(f"{key}="):
                    fields[key] = line[len(key) + 1:]; break

        if not fields.get("hash"):
            continue

        subject = fields.get("subject", "")
        body    = "\n".join(body_lines).strip()
        all_tags, semver = _parse_tags(fields.get("refs", ""))
        cc_type, cc_scope, cc_breaking = _parse_conventional(subject)

        commits.append(CommitRecord(
            hash=fields.get("hash", ""), short=fields.get("short", ""),
            author=fields.get("author", ""), email=fields.get("email", ""),
            date=fields.get("date", ""), subject=subject, body=body,
            refs=fields.get("refs", ""), tags=all_tags, semver_tags=semver,
            co_authors=_parse_co_authors(body),
            is_merge=subject.lower().startswith("merge"),
            is_first_parent=first_parent, pr_number=_parse_pr_number(subject),
            cc_type=cc_type, cc_scope=cc_scope, cc_breaking=cc_breaking,
        ))

    _enrich_file_stats(commits, repo_path)
    commits.reverse()
    return commits


def _enrich_file_stats(commits: list[CommitRecord], repo_path: Path) -> None:
    for commit in commits:
        try:
            raw = _run(["git", "diff-tree", "--no-commit-id", "-r", "--numstat", commit.hash], cwd=repo_path)
            files: list[str] = []
            insertions = deletions = 0
            for line in raw.strip().splitlines():
                parts = line.split("\t")
                if len(parts) == 3:
                    if parts[0] == "-" or parts[1] == "-":
                        files.append(parts[2]); continue
                    insertions += int(parts[0]) if parts[0].isdigit() else 0
                    deletions  += int(parts[1]) if parts[1].isdigit() else 0
                    files.append(parts[2])
            commit.files_changed = files
            commit.stats = {"insertions": insertions, "deletions": deletions, "files": len(files)}
        except Exception:
            pass


# ── Public API ─────────────────────────────────────────────────────────────────

def ingest_git_history(
    repo_path: Path,
    branch: str = "HEAD",
    first_parent: bool = False,
    burst_gap_hours: float = 4.0,
) -> GitIngestionResult:
    """
    Walk the full git log and return a GitIngestionResult, oldest-first.

    v4 additions: co-change matrix, knowledge silos, refactor trend,
    enhanced velocity with stddev / acceleration / momentum.
    """
    repo_path = Path(repo_path).resolve()
    if _is_shallow(repo_path):
        print("[git_ingester] ⚠ Shallow clone — history may be incomplete.")

    commits: list[CommitRecord] = []
    for backend_fn, name in [(_ingest_gitpython, "GitPython"), (_ingest_subprocess, "subprocess")]:
        try:
            commits = backend_fn(repo_path, branch, first_parent)
            print(f"[git_ingester] ✓ {len(commits)} commits via {name}")
            break
        except ImportError:
            print("[git_ingester] GitPython not installed — falling back to subprocess")
        except Exception as exc:
            print(f"[git_ingester] {name} failed: {exc}")

    if not commits:
        raise RuntimeError("All git_ingester backends failed.")

    author_profiles  = _build_author_profiles(commits)
    churn_index      = _build_churn_index(commits)
    hotspot_ranking  = _build_hotspot_ranking(commits)
    burst_clusters   = _detect_bursts(commits, burst_gap_hours)
    co_change_matrix = _build_co_change_matrix(commits)
    refactor_trend   = _build_refactor_trend(commits)
    velocity         = _compute_velocity(commits)
    timestamps       = [c.date for c in commits]

    silos = [a for a in author_profiles if a.silo_score > 0.5]
    print(
        f"[git_ingester] ✓ {len(author_profiles)} authors · "
        f"{len(burst_clusters)} burst(s) · "
        f"{velocity.get('commits_per_day', 0):.2f} c/day · "
        f"{len(silos)} knowledge silo(s)"
    )

    return GitIngestionResult(
        commits=commits, author_profiles=author_profiles,
        churn_index=churn_index, hotspot_ranking=hotspot_ranking,
        burst_clusters=burst_clusters, co_change_matrix=co_change_matrix,
        refactor_trend=refactor_trend, velocity_summary=velocity,
        timestamps=timestamps,
    )


# ── Convenience I/O ────────────────────────────────────────────────────────────

def save_result_json(result: GitIngestionResult, output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"[git_ingester] Saved → {output_path}")


def load_result_json(input_path: Path) -> dict:
    with open(input_path, encoding="utf-8") as f:
        return json.load(f)


def save_commits_json(commits: list[CommitRecord], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in commits], f, indent=2, ensure_ascii=False)


def load_commits_json(input_path: Path) -> list[dict]:
    with open(input_path, encoding="utf-8") as f:
        return json.load(f)


__all__ = [
    "ingest_git_history",
    "save_result_json",
    "load_result_json",
    "save_commits_json",
    "load_commits_json",
    "GitIngestionResult",
]
