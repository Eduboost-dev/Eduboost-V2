# DB Migration + Seed Repeatability Status

Generated at: `2026-06-04T11:17:34Z`
Commit: `1faa5ed5f7e4961d9d8cc7f666684057494eb8fb`

**Status:** `db-migration-seed-repeatability-not-proven`
**Raw Alembic SQL:** `temp/db_repeatability/alembic_upgrade_head.raw.sql`
**Supabase SQL:** `temp/db_repeatability/alembic_upgrade_head.supabase.sql`
**IRT seed SQL:** `temp/db_repeatability/seed_irt_items.sql`

## Summary

- Alembic head `20260516_0100` present: `False`
- Raw SQL lines: `11`
- Supabase SQL lines: `11`
- Removed chatter lines: `0`
- Removed broken null seed blocks: `0`
- Removed Supabase role lines: `0`
- Generated IRT seed rows: `1600`
- Unique IRT seed rows: `1600`

## Required runtime tables

| Table | DDL present |
|---|---:|
| `audit_events` | False |
| `audit_logs` | False |
| `calibration_audits` | False |
| `diagnostic_items` | False |
| `diagnostic_sessions` | False |
| `guardians` | False |
| `irt_items` | False |
| `item_exposures` | False |
| `knowledge_gaps` | False |
| `learner_profiles` | False |
| `lesson_feedback` | False |
| `lessons` | False |
| `mastery_snapshots` | False |
| `parental_consents` | False |
| `practice_queue` | False |
| `rlhf_exports` | False |
| `spaced_review_schedule` | False |
| `stripe_webhook_events` | False |
| `subject_mastery` | False |
| `topic_mastery` | False |

## Apply commands

```bash
# Generate checked SQL artifacts
make db-migration-seed-repeatability-status

# Apply manually to linked Supabase after review
npx --yes supabase db query --linked --file temp/db_repeatability/alembic_upgrade_head.supabase.sql
npx --yes supabase db query --linked --file temp/db_repeatability/seed_irt_items.sql
```

## Blockers

- alembic upgrade head --sql failed
- expected Alembic head 20260516_0100 missing from generated SQL
- required runtime table DDL missing: audit_events, audit_logs, calibration_audits, diagnostic_items, diagnostic_sessions, guardians, irt_items, item_exposures, knowledge_gaps, learner_profiles, lesson_feedback, lessons, mastery_snapshots, parental_consents, practice_queue, rlhf_exports, spaced_review_schedule, stripe_webhook_events, subject_mastery, topic_mastery

## No false-closure rules

- This proves repeatable generation of Supabase-safe migration and IRT seed SQL.
- It does not prove remote apply unless the generated SQL is applied and verified separately.
- It does not decide whether `diagnostic_items` should be populated.
- It does not decide ownership of live-only POPIA/DSR tables.
- It does not prove audit writes or backup/restore/rollback posture.
