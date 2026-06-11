# Phase 5 Execution Plan — Migrations and Schema Management

**Date**: 2026-06-10
**Status**: IN PROGRESS
**Branch**: `phase-5/migrations-and-schema-management`
**Scope**: Fix broken migration graph, remove production startup schema repair, add migration verification to CI.
**Priority**: P1 (per [roadmap.md](../roadmap.md#L231-L253))

---

## Pre-Conditions

Before Phase 5 implementation begins:

- [ ] Repair the local virtual environment: `.venv/bin/python` is 0 bytes.
  ```bash
  python -m venv .venv
  .venv/bin/pip install -e ".[dev]"
  ```
  **Current state:** `python` (system) = 3.13.12; `.venv/bin/python` = 0 bytes (broken symlink).

---

## Pre-Execution Baseline

### 5.0.1 — Migration Graph Check (captured 2026-06-10)

```bash
$ python scripts/verify_migration_graph.py
```

**Actual output (baseline — FAILING):**

```
Migration graph validation failed:
- 20260609_0800_practice_sessions_durable.py: down_revision '20260605_0500_fix_migration_graph' does not exist
- 3f8a2c1d9e04_add_auth_extensions.py: new migration names must match YYYYMMDD_HHMM_<short_description>.py
- f2faf5aa12fd_merge_migration_branches.py: new migration names must match YYYYMMDD_HHMM_<short_description>.py
- expected exactly one head revision, found ['20260609_0800_practice_sessions_durable', 'f2faf5aa12fd']
```

4 errors, exit code 1. Two distinct root causes:
1. Broken `down_revision` pointer (`20260605_0500_fix_migration_graph` ghost reference)
2. Two legacy migrations not registered in `LEGACY_EXEMPTIONS`

### 5.0.2 — Startup Schema Repair (code inspection)

The function `run_startup_migrations()` at [app/api_v2.py](../../app/api_v2.py#L35-L115) runs **only in production** (`if not settings.is_production(): return`). It performs DDL against the live database:

- `ALTER TABLE guardians ADD COLUMN IF NOT EXISTS email_verified`
- `CREATE TYPE tokenpurpose AS ENUM (...)`
- `CREATE TABLE IF NOT EXISTS secure_tokens (...)`
- `CREATE UNIQUE INDEX IF NOT EXISTS ...`

This means production database schema is mutated on every API restart outside of Alembic's control. The migration responsibility is split between Alembic (for dev/CI) and this startup repair (for production).

### 5.0.3 — CI Coverage

Static migration graph validation and schema integrity checks are **not present** in `.github/workflows/ci-cd.yml`. No CI job blocks on migration correctness.

---

## Phase 5.1 — Fix Broken Migration Graph

### Problem Statement

`python scripts/verify_migration_graph.py` fails with 4 errors. The practice-sessions migration references a non-existent parent, and two legacy migrations violate the naming convention without being exempted.

### Acceptance Criteria

- [ ] `python scripts/verify_migration_graph.py` passes with 0 errors
- [ ] Migration graph resolves to exactly one head revision

### Implementation Tasks

- [ ] Fix `down_revision` in [alembic/versions/20260609_0800_practice_sessions_durable.py](../../alembic/versions/20260609_0800_practice_sessions_durable.py): change `'20260605_0500_fix_migration_graph'` → `'f2faf5aa12fd'`
- [ ] Add `"3f8a2c1d9e04_add_auth_extensions.py"` to `LEGACY_EXEMPTIONS` in [scripts/verify_migration_graph.py](../../scripts/verify_migration_graph.py)
- [ ] Add `"f2faf5aa12fd_merge_migration_branches.py"` to `LEGACY_EXEMPTIONS`
- [ ] Run `python scripts/verify_migration_graph.py` — confirm 0 errors, exit code 0
- [ ] Commit with message: `fix: repair migration graph (down_revision + legacy exemptions)`

---

## Phase 5.2 — Remove Production Startup Schema Repair

### Problem Statement

`run_startup_migrations()` in [app/api_v2.py](../../app/api_v2.py#L35) mutates the production database schema on every API restart. This is dangerous because:

- DDL runs against a live production database without migration tracking
- Schema state depends on which API instance restarts first
- Alembic has no visibility into these mutations
- The function is conditional on `settings.is_production()` — meaning it only runs where it's most dangerous

### Acceptance Criteria

- [ ] `run_startup_migrations()` function removed from [app/api_v2.py](../../app/api_v2.py)
- [ ] `lifespan` context manager no longer calls any schema mutation
- [ ] All schema objects created by `run_startup_migrations` are covered by existing Alembic migrations (verified via `alembic upgrade head` against a fresh database)
- [ ] API startup produces no DDL statements against the database

### Implementation Tasks

- [ ] Verify that Alembic migrations already cover: `guardians.email_verified`, `tokenpurpose` enum, `secure_tokens` table, and indexes
- [ ] Delete the `run_startup_migrations()` function from [app/api_v2.py](../../app/api_v2.py)
- [ ] Remove the call to `run_startup_migrations()` from the `lifespan` context manager
- [ ] Clean up unused imports resulting from the removal
- [ ] Commit with message: `fix: remove production startup schema repair (Alembic is authoritative)`

---

## Phase 5.3 — Prove Migration Correctness Against a Live Database

### Problem Statement

The RoadMap requires proof that `alembic upgrade head` succeeds in an isolated test database and that `alembic current` reports the expected head. This has not been demonstrated.

### Acceptance Criteria

- [ ] `alembic upgrade head` succeeds in an isolated test database (Docker PostgreSQL or local)
- [ ] `alembic current --verbose` reports a single head revision matching the latest migration
- [ ] `make migration-smoke` passes (upgrade → downgrade → upgrade cycle)

### Implementation Tasks

- [ ] Start a disposable PostgreSQL instance (Docker or local)
- [ ] Run `alembic upgrade head` — capture output
- [ ] Run `alembic current --verbose` — capture output showing single head
- [ ] Run `alembic downgrade -1` then `alembic upgrade head` to verify downgrade path
- [ ] Capture all output to `docs/release/phase_5_evidence.md`
- [ ] Commit evidence file

---

## Phase 5.4 — Add Migration Checks to CI

### Problem Statement

`verify_migration_graph.py` and `validate_schema_integrity.py` exist but are not executed as blocking steps in the CI/CD pipeline. Schema drift can reach `master` undetected.

### Acceptance Criteria

- [ ] `python scripts/verify_migration_graph.py` runs as a blocking step in CI
- [ ] `python scripts/validate_schema_integrity.py` runs as a blocking step in CI
- [ ] CI job fails if either script exits non-zero

### Implementation Tasks

- [ ] Add a `schema-drift` job (or extend existing `lint` job) in [.github/workflows/ci-cd.yml](../../.github/workflows/ci-cd.yml):
  ```yaml
  - name: Migration Graph Check
    run: python scripts/verify_migration_graph.py
  - name: Schema Integrity Check
    run: python scripts/validate_schema_integrity.py
  ```
- [ ] Commit CI config change

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 5 evidence (before/after migration checks) | `docs/release/phase_5_evidence.md` | [ ] |
| CI run URL with passing schema checks | Captured from PR | [verify] |
| Implementation audit | `docs/release/phase_5_implementation_audit.md` | [ ] |

---

## Success Criteria

**Phase 5 is complete when:**

- [ ] `python scripts/verify_migration_graph.py` passes with 0 errors
- [ ] `alembic upgrade head` succeeds against an isolated database
- [ ] `alembic current --verbose` reports a single expected head
- [ ] API startup performs zero DDL (no schema repair in `lifespan`)
- [ ] CI blocks on migration graph and schema integrity checks
- [ ] All evidence files committed
- [ ] `docs/release/phase_5_implementation_audit.md` committed
- [ ] Tracking documents updated (`roadmap.md`, `build-plan.md`, `progress-tracker.md`, `todo.md`)

---

## Close Checklist (per PROCESS_DISCIPLINE.md)

- [ ] Execution plan exists: `docs/roadmap/execution/phase_5_execution_plan.md` (this file)
- [ ] Implementation report exists: `docs/roadmap/execution/phase_5_implementation_report.md`
- [ ] Audit report exists: `docs/release/phase_5_implementation_audit.md`
- [ ] Evidence files committed and accurate
- [ ] `roadmap.md` Phase 5 status updated to "Complete (YYYY-MM-DD)"
- [ ] `context/build-plan.md` Phase 5 status updated
- [ ] `context/progress-tracker.md` updated
- [ ] CI gates pass on the phase branch
- [ ] Branch merged to `master` via PR
- [ ] Remote branch deleted after merge
- [ ] `docs/todos/todo.md` North Star tasks updated

---

## Next Phase

**Phase 6: Durable Background Jobs** — Wire ARQ durable background worker into Compose/Production. Replace non-durable FastAPI `BackgroundTasks` with durable jobs.

---

## References

- RoadMap Phase 5: [roadmap.md](../roadmap.md#L231)
- Process Discipline: [PROCESS_DISCIPLINE.md](../PROCESS_DISCIPLINE.md)
- Migration graph script: [scripts/verify_migration_graph.py](../../scripts/verify_migration_graph.py)
- Startup repair code: [app/api_v2.py](../../app/api_v2.py#L35-L115)
- CI workflow: [.github/workflows/ci-cd.yml](../../.github/workflows/ci-cd.yml)
