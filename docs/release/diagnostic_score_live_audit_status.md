# Diagnostic Score Live Audit Status

Generated at: `2026-05-22T20:38:29Z`
Commit: `e3386f8380b268d23b30dc067ce5c65e3acf54ba`

**Status:** `diagnostic-score-live-audit-not-accepted`
**DB URL label:** ``
**DB checked:** `False`
**Seed attempted:** `False`
**Seed inserted rows:** `0`
**diagnostic_items count:** `None`
**irt_items count:** `None`
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``
**Test command:** ``
**Seed result:** ``
**Scoring result:** ``
**Audit result:** ``

## Bridge seed columns

- None

## Unsupported required columns

- None

## diagnostic_items columns

| Column | Nullable | Default | Type | UDT |
|---|---:|---:|---|---|

## Blockers

- DIAG_SCORE_DATABASE_URL/DATABASE_URL is missing, non-Postgres async, local, example, or placeholder

## No false-closure rules

- This proof closes DIAG-SCORE-001 only in DIAG_SCORE_ACCEPT=1 mode.
- Live DB mutation requires DIAG_SCORE_ALLOW_BRIDGE_SEED=1.
- diagnostic_items must have rows after seed/audit.
- Scoring and audit result metadata must be explicit.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close JWT, ARQ, approvals, frontend runtime, audit-write, backup/restore/rollback, or beta release.
