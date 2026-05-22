from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.parse import urlparse
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/release/diagnostic_score_live_audit_status.json"
STATUS_MD = ROOT / "docs/release/diagnostic_score_live_audit_status.md"

ACCEPTED_STATUS = "diagnostic-score-live-audit-accepted"
NOT_ACCEPTED_STATUS = "diagnostic-score-live-audit-not-accepted"

EXPECTED_IRT_MIN_ROWS = 1600
DIAG_TABLE = "diagnostic_items"
IRT_TABLE = "irt_items"

PLACEHOLDER_TOKENS = {
    "<",
    ">",
    "TODO",
    "TBD",
    "REAL_",
    "example.com",
    "localhost",
    "127.0.0.1",
    "...",
}


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    is_nullable: bool
    has_default: bool
    data_type: str
    udt_name: str


@dataclass(frozen=True)
class GitHubRunEvidence:
    run_id: str
    run_url: str
    workflow_name: str
    run_status: str
    conclusion: str
    head_sha: str
    blockers: list[str]


@dataclass(frozen=True)
class DiagnosticScoreLiveAuditStatus:
    generated_at: str
    current_commit: str
    status: str
    db_url_label: str
    db_checked: bool
    seed_attempted: bool
    seed_inserted_rows: int
    diagnostic_items_count: int | None
    irt_items_count: int | None
    diagnostic_items_columns: list[ColumnInfo]
    bridge_seed_columns: list[str]
    unsupported_required_columns: list[str]
    github_run: GitHubRunEvidence
    test_command: str
    seed_result: str
    scoring_result: str
    audit_result: str
    verified_by: str
    date_verified: str
    blockers: list[str]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)


def _db_url() -> tuple[str, str]:
    for name in [
        "DIAG_SCORE_DATABASE_URL",
        "DATABASE_URL",
        "STAGING_DATABASE_URL",
        "SUPABASE_DB_URL",
    ]:
        value = _env(name)
        if value:
            return name, normalize_db_url(value)
    return "", ""


def normalize_db_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


def _valid_db_url(url: str) -> bool:
    # By default, placeholder values (localhost, example, etc.) are rejected
    # to ensure proof runs against a real managed DB. For local development or
    # when the operator explicitly allows it, set `DIAG_SCORE_ALLOW_LOCAL=1`
    # in the environment to bypass this guard.
    if not url or _has_placeholder(url):
        if os.getenv("DIAG_SCORE_ALLOW_LOCAL") == "1":
            return True
        return False
    parsed = urlparse(url)
    return parsed.scheme == "postgresql+asyncpg" and bool(parsed.hostname)


def _quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


async def _table_exists(conn, table_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
              SELECT 1
              FROM information_schema.tables
              WHERE table_schema = 'public'
                AND table_name = :table_name
            )
            """
        ),
        {"table_name": table_name},
    )
    return bool(result.scalar_one())


async def _table_count(conn, table_name: str) -> int:
    result = await conn.execute(text(f"SELECT COUNT(*) FROM public.{_quote_ident(table_name)}"))
    return int(result.scalar_one())


async def _columns(conn, table_name: str) -> list[ColumnInfo]:
    result = await conn.execute(
        text(
            """
            SELECT
              column_name,
              is_nullable,
              column_default,
              data_type,
              udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
            ORDER BY ordinal_position
            """
        ),
        {"table_name": table_name},
    )
    return [
        ColumnInfo(
            name=str(row.column_name),
            is_nullable=str(row.is_nullable).upper() == "YES",
            has_default=row.column_default is not None,
            data_type=str(row.data_type),
            udt_name=str(row.udt_name),
        )
        for row in result
    ]


def _json_empty_for(column: ColumnInfo) -> str:
    if column.udt_name in {"json", "jsonb"} or column.data_type in {"json", "jsonb"}:
        return "'{}'::jsonb" if column.udt_name == "jsonb" else "'{}'::json"
    return _sql_literal("{}")


def _expr_for_diag_column(column: ColumnInfo, irt_columns: set[str]) -> str | None:
    name = column.name

    if name in irt_columns:
        # Some IRT columns need casting when inserted into diagnostic schema
        if name == "subject":
            return f"i.{_quote_ident(name)}::subjectcode"
        if name == "review_status":
            return f"i.{_quote_ident(name)}::reviewstatus"
        return f"i.{_quote_ident(name)}"

    if name == "item_id" and "id" in irt_columns:
        # diagnostic_items.item_id is a UUID; IRT ids are strings. Generate
        # a fresh UUID for the diagnostic item to avoid type mismatch.
        return "gen_random_uuid()"

    if name == "id" and "id" in irt_columns:
        return 'i."id"'

    if name in {"created_at", "updated_at"}:
        return "NOW()"

    if name in {"active", "is_active", "enabled"}:
        return "TRUE"

    if name in {"metadata", "tags", "properties"}:
        return _json_empty_for(column)

    if name == "caps_reference":
        if "topic" in irt_columns:
            return 'COALESCE(i."topic", i."id")'
        return 'i."id"'

    # Map diagnostic schema's shortened CAPS reference and other runtime-required
    # fields to reasonable defaults or IRT equivalents when possible.
    if name == "caps_ref":
        # Use the longer caps_reference from the IRT table, truncated to 40 chars
        if "caps_reference" in irt_columns:
            return 'LEFT(i."caps_reference", 40)'
        if "topic" in irt_columns:
            return 'LEFT(i."topic", 40)'
        return 'LEFT(i."id", 40)'

    if name == "term":
        # No term in IRT; default to term 1 for seeding
        return '1'

    if name == "subtopic":
        # Use the IRT topic as a fallback for subtopic
        if "topic" in irt_columns:
            return 'i."topic"'
        return _sql_literal("")

    if name == "stem":
        if "question_text" in irt_columns:
            return 'i."question_text"'
        return _sql_literal("")

    if name == "answer_key":
        # Use the single-letter correct_option as the answer key
        if "correct_option" in irt_columns:
            return 'i."correct_option"'
        return _sql_literal("")

    if name == "subject":
        # Cast IRT subject string into the diagnostic subjectcode enum when
        # possible, otherwise fall back to an explicit literal.
        if "subject" in irt_columns:
            return 'i."subject"::subjectcode'
        return _sql_literal("unknown")

    if name == "review_status":
        # Use a conservative default review status for seeded items
        return _sql_literal("draft")

    if name in {"difficulty", "bloom_level"} and "b_param" in irt_columns:
        return 'i."b_param"'

    if name in {"item_type", "type"}:
        # Map to a valid `itemtype` enum value; IRT bank contains MCQ items.
        return _sql_literal("mcq")

    if name in {"source", "origin"}:
        return _sql_literal("irt_items_bridge")

    if column.is_nullable or column.has_default:
        return None

    return "__UNSUPPORTED_REQUIRED__"


async def _bridge_seed(conn, diag_columns: list[ColumnInfo], irt_columns: list[ColumnInfo]) -> tuple[int, list[str], list[str]]:
    irt_names = {column.name for column in irt_columns}
    insert_columns: list[str] = []
    select_exprs: list[str] = []
    unsupported: list[str] = []

    for column in diag_columns:
        expr = _expr_for_diag_column(column, irt_names)
        if expr is None:
            continue
        if expr == "__UNSUPPORTED_REQUIRED__":
            unsupported.append(column.name)
            continue
        insert_columns.append(column.name)
        select_exprs.append(expr)

    if unsupported:
        return 0, insert_columns, unsupported

    if not insert_columns:
        return 0, insert_columns, ["no insertable diagnostic_items columns found"]

    sql = (
        f"INSERT INTO public.{_quote_ident(DIAG_TABLE)} "
        f"({', '.join(_quote_ident(column) for column in insert_columns)}) "
        f"SELECT {', '.join(select_exprs)} "
        f"FROM public.{_quote_ident(IRT_TABLE)} i "
        "ON CONFLICT DO NOTHING"
    )
    result = await conn.execute(text(sql))
    return int(result.rowcount or 0), insert_columns, []


def _parse_json(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return fallback


def _gh_available() -> bool:
    return _run(["gh", "--version"]).returncode == 0


def _view_run(run_id: str) -> dict[str, Any] | None:
    result = _run(
        [
            "gh",
            "run",
            "view",
            run_id,
            "--json",
            "databaseId,status,conclusion,headSha,url,workflowName,createdAt",
        ]
    )
    if result.returncode != 0:
        return None
    data = _parse_json(result.stdout, None)
    return data if isinstance(data, dict) else None


def collect_github_run_evidence(run_id: str, expected_sha: str) -> GitHubRunEvidence:
    blockers: list[str] = []

    if not run_id:
        blockers.append("DIAG_SCORE_RUN_ID is required for accepted evidence")
        return GitHubRunEvidence("", "", "", "", "", "", blockers)

    if not re.fullmatch(r"[0-9]+", run_id):
        blockers.append("DIAG_SCORE_RUN_ID is not numeric")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)

    if not _gh_available():
        blockers.append("GitHub CLI is unavailable or not authenticated")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)

    run = _view_run(run_id)
    if run is None:
        blockers.append(f"unable to read GitHub Actions run {run_id}")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)

    run_url = str(run.get("url") or f"https://github.com/NkgoloL/Eduboost-V2/actions/runs/{run_id}").strip()
    workflow_name = str(run.get("workflowName") or "").strip()
    run_status = str(run.get("status") or "").strip()
    conclusion = str(run.get("conclusion") or "").strip()
    head_sha = str(run.get("headSha") or "").strip()

    if f"/actions/runs/{run_id}" not in run_url:
        blockers.append("run URL does not contain numeric run ID")
    if run_status != "completed":
        blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")
    if conclusion != "success":
        blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")
    if head_sha != expected_sha:
        blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")
    if not workflow_name:
        blockers.append("workflow name is missing")

    return GitHubRunEvidence(
        run_id=run_id,
        run_url=run_url,
        workflow_name=workflow_name,
        run_status=run_status,
        conclusion=conclusion,
        head_sha=head_sha,
        blockers=blockers,
    )


async def collect_status(*, apply_seed: bool) -> DiagnosticScoreLiveAuditStatus:
    blockers: list[str] = []
    sha = current_commit()

    db_url_label, db_url = _db_url()
    db_checked = False
    seed_attempted = False
    seed_inserted = 0
    diagnostic_count: int | None = None
    irt_count: int | None = None
    diag_columns: list[ColumnInfo] = []
    bridge_columns: list[str] = []
    unsupported_required: list[str] = []

    if not _valid_db_url(db_url):
        blockers.append("DIAG_SCORE_DATABASE_URL/DATABASE_URL is missing, non-Postgres async, local, example, or placeholder")
    else:
        engine = create_async_engine(db_url, pool_pre_ping=True)
        try:
            async with engine.begin() as conn:
                db_checked = True
                diag_exists = await _table_exists(conn, DIAG_TABLE)
                irt_exists = await _table_exists(conn, IRT_TABLE)

                if not diag_exists:
                    blockers.append("diagnostic_items table is missing")
                if not irt_exists:
                    blockers.append("irt_items table is missing")

                if diag_exists:
                    diag_columns = await _columns(conn, DIAG_TABLE)
                    diagnostic_count = await _table_count(conn, DIAG_TABLE)

                if irt_exists:
                    irt_columns = await _columns(conn, IRT_TABLE)
                    irt_count = await _table_count(conn, IRT_TABLE)
                else:
                    irt_columns = []

                if irt_count is not None and irt_count < EXPECTED_IRT_MIN_ROWS:
                    blockers.append(f"irt_items has {irt_count} rows, expected at least {EXPECTED_IRT_MIN_ROWS}")

                if apply_seed:
                    seed_attempted = True
                    if _env("DIAG_SCORE_ALLOW_BRIDGE_SEED") != "1":
                        blockers.append("DIAG_SCORE_ALLOW_BRIDGE_SEED must be 1 before mutating diagnostic_items")
                    elif not diag_exists or not irt_exists:
                        blockers.append("cannot bridge-seed without both diagnostic_items and irt_items")
                    else:
                        seed_inserted, bridge_columns, unsupported_required = await _bridge_seed(
                            conn,
                            diag_columns,
                            irt_columns,
                        )
                        if unsupported_required:
                            blockers.append(
                                "unsupported required diagnostic_items columns for bridge seed: "
                                + ", ".join(unsupported_required)
                            )
                        diagnostic_count = await _table_count(conn, DIAG_TABLE)

                if diagnostic_count is None or diagnostic_count <= 0:
                    blockers.append("diagnostic_items has 0 rows; runtime-required item bank is not seeded")

        finally:
            await engine.dispose()

    test_command = _env("DIAG_SCORE_TEST_COMMAND")
    seed_result = _env("DIAG_SCORE_SEED_RESULT")
    scoring_result = _env("DIAG_SCORE_SCORING_RESULT")
    audit_result = _env("DIAG_SCORE_AUDIT_RESULT")

    if _env("DIAG_SCORE_ACCEPT") == "1":
        if not test_command or _has_placeholder(test_command):
            blockers.append("DIAG_SCORE_TEST_COMMAND is missing or placeholder")
        if seed_result != "passed":
            blockers.append("DIAG_SCORE_SEED_RESULT must be passed")
        if scoring_result != "passed":
            blockers.append("DIAG_SCORE_SCORING_RESULT must be passed")
        if audit_result != "passed":
            blockers.append("DIAG_SCORE_AUDIT_RESULT must be passed")
        github = collect_github_run_evidence(_env("DIAG_SCORE_RUN_ID"), sha)
        blockers.extend(github.blockers)
    else:
        github = GitHubRunEvidence("", "", "", "", "", "", [])

    status = ACCEPTED_STATUS if _env("DIAG_SCORE_ACCEPT") == "1" and not blockers else NOT_ACCEPTED_STATUS

    return DiagnosticScoreLiveAuditStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=sha,
        status=status,
        db_url_label=db_url_label,
        db_checked=db_checked,
        seed_attempted=seed_attempted,
        seed_inserted_rows=seed_inserted,
        diagnostic_items_count=diagnostic_count,
        irt_items_count=irt_count,
        diagnostic_items_columns=diag_columns,
        bridge_seed_columns=bridge_columns,
        unsupported_required_columns=unsupported_required,
        github_run=github,
        test_command=test_command,
        seed_result=seed_result,
        scoring_result=scoring_result,
        audit_result=audit_result,
        verified_by="github-actions" if status == ACCEPTED_STATUS else "unverified",
        date_verified=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        blockers=blockers,
    )


def write_status(*, apply_seed: bool = False) -> DiagnosticScoreLiveAuditStatus:
    status = asyncio.run(collect_status(apply_seed=apply_seed))
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    _write_markdown(status)
    return status


def _write_markdown(status: DiagnosticScoreLiveAuditStatus) -> None:
    lines = [
        "# Diagnostic Score Live Audit Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**DB URL label:** `{status.db_url_label}`",
        f"**DB checked:** `{status.db_checked}`",
        f"**Seed attempted:** `{status.seed_attempted}`",
        f"**Seed inserted rows:** `{status.seed_inserted_rows}`",
        f"**diagnostic_items count:** `{status.diagnostic_items_count}`",
        f"**irt_items count:** `{status.irt_items_count}`",
        f"**Run ID:** `{status.github_run.run_id}`",
        f"**Run URL:** `{status.github_run.run_url}`",
        f"**Workflow:** `{status.github_run.workflow_name}`",
        f"**Test command:** `{status.test_command}`",
        f"**Seed result:** `{status.seed_result}`",
        f"**Scoring result:** `{status.scoring_result}`",
        f"**Audit result:** `{status.audit_result}`",
        "",
        "## Bridge seed columns",
        "",
    ]

    if status.bridge_seed_columns:
        lines.extend(f"- `{column}`" for column in status.bridge_seed_columns)
    else:
        lines.append("- None")

    lines.extend(["", "## Unsupported required columns", ""])
    if status.unsupported_required_columns:
        lines.extend(f"- `{column}`" for column in status.unsupported_required_columns)
    else:
        lines.append("- None")

    lines.extend(["", "## diagnostic_items columns", "", "| Column | Nullable | Default | Type | UDT |", "|---|---:|---:|---|---|"])
    for column in status.diagnostic_items_columns:
        lines.append(
            f"| `{column.name}` | {column.is_nullable} | {column.has_default} | `{column.data_type}` | `{column.udt_name}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- This proof closes DIAG-SCORE-001 only in DIAG_SCORE_ACCEPT=1 mode.",
            "- Live DB mutation requires DIAG_SCORE_ALLOW_BRIDGE_SEED=1.",
            "- diagnostic_items must have rows after seed/audit.",
            "- Scoring and audit result metadata must be explicit.",
            "- A successful GitHub Actions run matching current commit is required.",
            "- This proof does not close JWT, ARQ, approvals, frontend runtime, audit-write, backup/restore/rollback, or beta release.",
            "",
        ]
    )

    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-seed", action="store_true")
    args = parser.parse_args()

    result = write_status(apply_seed=args.apply_seed)
    print(result.status)
    print(f"diagnostic_items_count={result.diagnostic_items_count}")
    print(f"irt_items_count={result.irt_items_count}")
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
