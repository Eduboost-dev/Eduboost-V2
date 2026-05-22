# Diagnostic Score Live Audit Status

Generated at: `2026-05-22T14:18:32Z`
Commit: `ec48d99ff48d4ad08572fa300cd0d50b25fbc0ec`

**Status:** `diagnostic-score-live-audit-not-accepted`
**DB URL label:** `DIAG_SCORE_DATABASE_URL`
**DB checked:** `True`
**Seed attempted:** `True`
**Seed inserted rows:** `0`
**diagnostic_items count:** `None`
**irt_items count:** `None`
**Run ID:** `26292735463`
**Run URL:** `https://github.com/NkgoloL/Eduboost-V2/actions/runs/26292735463`
**Workflow:** `Backend Consolidation Evidence`
**Test command:** `python scripts/diagnostic_score_live_audit.py --apply-seed`
**Seed result:** `0 rows inserted (local DB; remote import pending)`
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

- diagnostic_items table is missing
- irt_items table is missing
- cannot bridge-seed without both diagnostic_items and irt_items
- diagnostic_items has 0 rows; runtime-required item bank is not seeded

## No false-closure rules

- This proof closes DIAG-SCORE-001 only in DIAG_SCORE_ACCEPT=1 mode.
- Live DB mutation requires DIAG_SCORE_ALLOW_BRIDGE_SEED=1.
- diagnostic_items must have rows after seed/audit.
- Scoring and audit result metadata must be explicit.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close JWT, ARQ, approvals, frontend runtime, audit-write, backup/restore/rollback, or beta release.

## Supabase import helper

- Use `scripts/import_supabase_seed.sh` to import `scripts/irt_seed_1600.sql` into a Supabase Postgres instance. Copy `.env.supabase.example` to `.env.supabase` and set `SUPABASE_PG_PASSWORD` locally before running.

