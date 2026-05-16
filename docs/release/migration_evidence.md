# Database Migration Evidence

**Status:** pending runtime execution

This file records Alembic/schema migration execution against a disposable PostgreSQL database.

## Required environment

| Field | Value |
|---|---|
| Database name | TODO |
| Database host | TODO |
| Commit SHA | TODO |
| Alembic head before | TODO |
| Alembic head after | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| `alembic current` before upgrade | known baseline or empty DB | TODO |
| `alembic upgrade head` | succeeds | TODO |
| `alembic current` after upgrade | at repository head | TODO |
| schema integrity check | succeeds | TODO |
| migration graph check | single linear/resolvable head | TODO |
| downgrade/rollback path | succeeds or documented non-downgrade rationale | TODO |

## Command log

```bash
# paste commands and output here
```

## Decision

- [ ] Migration proof passed.
- [ ] Migration proof failed and release is blocked.
