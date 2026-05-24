# DB Backup / Restore / Rollback Evidence Status

Generated at: `2026-05-24T00:01:26Z`
Commit: `8b111c477a556247bd41221b8f30fb5ea8ef79f1`

**Status:** `db-backup-restore-rollback-accepted`
**Source DB:** `DB_ROLLBACK_SOURCE_DATABASE_URL:aws-0-eu-west-1.pooler.supabase.com:5432/postgres`
**Restore DB:** `DB_ROLLBACK_RESTORE_DATABASE_URL:172.19.0.2:5432/postgres`
**Dump label:** `db_rollback_8b111c477a55_20260524000020.dump`
**Dump SHA256:** `79b6d09d98e84b988483c80ef4cccda52c06040af73a4e68ccb06a87469feb96`
**Dump size bytes:** `311826`
**Source table count:** `26`
**Restore table count:** `26`
**Source Alembic:** `20260516_0100`
**Restore Alembic:** `20260516_0100`
**Run ID:** `26346124598`
**Run URL:** `https://github.com/NkgoloL/Eduboost-V2/actions/runs/26346124598`

## Key table counts

| Table | Source | Restore |
|---|---:|---:|
| `alembic_version` | 1 | 1 |
| `audit_events` | 6 | 6 |
| `diagnostic_items` | 0 | 0 |
| `irt_items` | 1600 | 1600 |
| `parental_consents` | 0 | 0 |

## Key count mismatches

- None

## Backup output excerpt

```text

```

## Restore output excerpt

```text

```

## Blockers

- None

## No false-closure rules

- DB-ROLLBACK-001 closes only in `DB_ROLLBACK_ACCEPT=1` mode.
- Source and restore database URLs must differ.
- Restore target must be disposable/staging, not production.
- Dump is not uploaded; checksum and status evidence only are persisted.
- Source and restore table count, Alembic version, and key table counts must match.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close JWT, ARQ, DIAG-SCORE, AUDIT-WRITE, approvals, frontend runtime, image/SBOM, security scans, or beta release.
