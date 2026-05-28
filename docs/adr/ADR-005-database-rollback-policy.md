# ADR-005 — Database Rollback Policy

Status: Proposed

## Context

Alembic forward upgrade to head is required for deployment. A previous downgrade-to-base test
failed because PostgreSQL enum types were still referenced by tables during downgrade.

## Decision

TBD. Choose exactly one supported rollback model:

1. Alembic downgrade is supported and must pass for all migrations.
2. Restore-from-backup / forward-fix is the supported production rollback path.

## Consequences

If option 1 is selected, enum downgrade ordering must be repaired.
If option 2 is selected, DR restore evidence must be kept current and downgrade may remain
unsupported for production rollback.
