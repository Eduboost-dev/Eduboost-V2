# Diagnostic Score Live Audit Status

Generated at: `2026-05-22T23:29:31Z`
Commit: `7f16b079bacfb08ff139314a42bf0abf37488c45`

**Status:** `diagnostic-score-live-audit-accepted`
**DB URL label:** `DIAG_SCORE_DATABASE_URL`
**DB checked:** `True`
**Seed attempted:** `True`
**Seed inserted rows:** `1600`
**diagnostic_items count:** `28800`
**irt_items count:** `1600`
**Run ID:** `26316648760`
**Run URL:** `https://github.com/NkgoloL/Eduboost-V2/actions/runs/26316648760`
**Workflow:** `.github/workflows/diag-score-live-audit.yml`
**Test command:** `python scripts/diagnostic_score_live_audit.py --apply-seed`
**Seed result:** `passed`
**Scoring result:** `passed`
**Audit result:** `passed`

## Bridge seed columns

- `item_id`
- `caps_ref`
- `grade`
- `subject`
- `term`
- `topic`
- `subtopic`
- `skill`
- `stem`
- `answer_key`
- `options`
- `explanation`
- `item_type`
- `language`
- `review_status`
- `source`
- `created_at`
- `updated_at`

## Unsupported required columns

- None

## diagnostic_items columns

| Column | Nullable | Default | Type | UDT |
|---|---:|---:|---|---|
| `item_id` | False | True | `uuid` | `uuid` |
| `caps_ref` | False | False | `character varying` | `varchar` |
| `grade` | False | False | `smallint` | `int2` |
| `subject` | False | False | `USER-DEFINED` | `subjectcode` |
| `term` | False | False | `smallint` | `int2` |
| `topic` | False | False | `character varying` | `varchar` |
| `subtopic` | False | False | `character varying` | `varchar` |
| `skill` | False | False | `character varying` | `varchar` |
| `stem` | False | False | `text` | `text` |
| `answer_key` | False | False | `character varying` | `varchar` |
| `options` | True | False | `jsonb` | `jsonb` |
| `explanation` | False | False | `text` | `text` |
| `distractor_rationale` | True | False | `jsonb` | `jsonb` |
| `misconception_tags` | False | True | `ARRAY` | `_text` |
| `item_type` | False | True | `USER-DEFINED` | `itemtype` |
| `language` | False | True | `USER-DEFINED` | `language` |
| `difficulty_b` | False | True | `numeric` | `numeric` |
| `discrimination_a` | False | True | `numeric` | `numeric` |
| `guessing_c` | False | True | `numeric` | `numeric` |
| `difficulty_band` | False | True | `USER-DEFINED` | `difficultyband` |
| `review_status` | False | True | `USER-DEFINED` | `reviewstatus` |
| `reviewer_id` | True | False | `uuid` | `uuid` |
| `reviewed_at` | True | False | `timestamp with time zone` | `timestamptz` |
| `exposure_count` | False | True | `integer` | `int4` |
| `max_exposure` | False | True | `integer` | `int4` |
| `quality_score` | True | False | `numeric` | `numeric` |
| `safety_passed` | False | True | `boolean` | `bool` |
| `source` | False | True | `USER-DEFINED` | `itemsource` |
| `created_at` | False | True | `timestamp with time zone` | `timestamptz` |
| `updated_at` | False | True | `timestamp with time zone` | `timestamptz` |

## Blockers

- None

## No false-closure rules

- This proof closes DIAG-SCORE-001 only in DIAG_SCORE_ACCEPT=1 mode.
- Live DB mutation requires DIAG_SCORE_ALLOW_BRIDGE_SEED=1.
- diagnostic_items must have rows after seed/audit.
- Scoring and audit result metadata must be explicit.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close JWT, ARQ, approvals, frontend runtime, audit-write, backup/restore/rollback, or beta release.
