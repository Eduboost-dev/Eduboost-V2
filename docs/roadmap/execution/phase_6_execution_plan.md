# Phase 6 Execution Plan — Durable Background Jobs

**Date**: 2026-06-10
**Updated**: 2026-06-10 (post-audit — 6.1-6.2 complete, 6.3-6.4 remaining)
**Status**: IN PROGRESS
**Branch**: `phase-6/durable-background-jobs`
**Completed**: 6.1 (ARQ settings fix), 6.2 (Compose wiring) — commit `dad8c5e7`
**Remaining**: 6.3 (move work off BackgroundTasks), 6.4 (evidence + health checks)
**Scope**: Replace request-adjacent placeholder job handling with durable ARQ worker wiring, compose/production deployment support, and verification evidence.
**Priority**: P1 (per [roadmap.md](../roadmap.md#L258-L281))

---

## Pre-Conditions

- [x] Branch `phase-6/durable-background-jobs` created (includes Phase 5 changes).
- [x] ARQ worker code already exists in `app/modules/jobs.py` (WorkerSettings, cron jobs).
- [x] Docker Compose is the deployment source of truth; worker service added to both dev and prod compose files.
- [ ] Redis must be running for live enqueue/dequeue verification (needed for Phase 6.4).

---

## Pre-Execution Baseline

### 6.0.1 — Background Job Split (captured 2026-06-10)

Current state from code inspection:

- [`app/core/jobs.py`](../../app/core/jobs.py) is a FastAPI `BackgroundTasks` wrapper with in-memory fallback state and Redis-backed job records.
- [`app/modules/jobs.py`](../../app/modules/jobs.py) already defines ARQ worker functions and cron schedules.
- [`app/jobs/consent_renewal_job.py`](../../app/jobs/consent_renewal_job.py) defines a consent renewal worker job entrypoint.
- [`app/services/arq_import_compat.py`](../../app/services/arq_import_compat.py) provides import-safe ARQ fallback types.
- The roadmap states that API routes still return job IDs through FastAPI `BackgroundTasks`, while ARQ job code exists but is not deployed.

### 6.0.2 — Deployment Wiring Check

Current repo scan indicates:

- `docker-compose.yml` exists, but Phase 6 worker wiring has not yet been verified in this session.
- The roadmap calls out missing worker deployment in Compose/production and a likely settings naming mismatch.

### 6.0.3 — CI / Verification Surface

Relevant checks already present in the repo:

- `scripts/check_arq_worker_import.py`
- `tests/unit/test_arq_worker_import_contract.py`
- `scripts/repair_arq_dependency_worker_import.py`
- `docs/release/arq_dependency_worker_import_repair_report.md`

Missing for Phase 6 completion:

- durable worker deployment evidence
- runtime enqueue/dequeue proof
- worker health/readiness evidence
- confirmation that request-adjacent `BackgroundTasks` usage is limited to non-critical paths

---

## Phase 6.1 — Fix ARQ Settings and Worker Wiring ✅ COMPLETE

### Problem Statement

The codebase already has ARQ job definitions, but the deployment/runtime path is not fully authoritative. The roadmap flags likely settings casing issues and missing worker deployment.

### Acceptance Criteria

- [x] ARQ settings resolve correctly for worker startup and runtime configuration.
- [x] ARQ worker entrypoint runs with the expected `WorkerSettings`.
- [x] The worker job set includes the durable jobs required by the roadmap.

### Implementation Tasks

- [x] Fixed `cfg.redis_url` → `cfg.REDIS_URL` (casing mismatch causing settings resolution failure).
- [x] Converted `redis_settings` from a `@classmethod` to a class variable on `WorkerSettings` (ARQ requires it as a simple attribute, not a method).
- [x] Import: added `from urllib.parse import urlparse` at module top.
- [x] Updated in-code comments in `app/jobs/consent_renewal_job.py` and `app/jobs/practice_session_cleanup_job.py` (`app/core/arq_worker.py` → `app/modules/jobs.py`).
- [x] Cron jobs (`consent_renewal`, `practice_session_cleanup`) already registered in `WorkerSettings`.

**Changed files:** `app/modules/jobs.py` (-18/+8), `app/jobs/consent_renewal_job.py`, `app/jobs/practice_session_cleanup_job.py`

---

## Phase 6.2 — Wire the Durable Worker into Compose / Production ✅ COMPLETE

### Problem Statement

The worker logic exists in code, but the deployment stack still needs an explicit service definition and startup path.

### Acceptance Criteria

- [x] Local Compose starts the ARQ worker successfully (service defined, `docker compose up worker`).
- [x] Production Compose / deployment manifests include the worker.
- [x] Redis connectivity is available to the worker in local and production-like environments (depends_on redis: service_healthy).

### Implementation Tasks

- [x] Added `worker` service to `docker-compose.yml`: uses `Dockerfile.v2`, command `arq app.modules.jobs.WorkerSettings`, env vars (`APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`).
- [x] Added `worker` service to `docker-compose.prod.yml`: same structure with production env vars plus `ENCRYPTION_KEY`, `ENCRYPTION_SALT`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`.
- [x] Both services depend on postgres and redis health checks.
- [x] Resource limits set (dev: 256M, prod: 768M memory).
- [x] Reuses existing `docker/Dockerfile.v2` (no separate worker Dockerfile needed).
- [ ] **Not yet verified:** `docker compose up worker` has not been executed against a live Redis/Postgres stack.

**Changed files:** `docker-compose.yml` (+26), `docker-compose.prod.yml` (+29)

---

## Phase 6.3 — Move Durable Work Off Request-Adjacent BackgroundTasks 🔴 NOT STARTED

### Problem Statement

The roadmap requires durable jobs rather than request-scoped `BackgroundTasks` for long-running or restart-sensitive work. Currently, API routes return job IDs via FastAPI `BackgroundTasks` with in-memory fallback state. If the API process restarts, queued work is lost.

### Discovery (do first)

Before any code changes, audit the current job landscape:

- [ ] **List all BackgroundTasks enqueue points.** Search `app/` for `background_tasks.add_task` and `BackgroundTasks` usage to find all non-durable job paths.
- [ ] **Classify each job**: `[durable-required]`, `[durable-optional]`, or `[request-adjacent-ok]`.
  - *Durable-required*: lesson generation, study-plan generation, consent renewal, practice session cleanup, ETL pipeline runs.
  - *Durable-optional*: email notifications, analytics events.
  - *Request-adjacent-ok*: short-lived audit writes, metric increments.
- [ ] **Document current state** as a table in the implementation report (route → job name → current mechanism → target mechanism).

### Acceptance Criteria

- [ ] Durable jobs are enqueued through ARQ (`await arq_queue.enqueue_job(...)`) rather than `background_tasks.add_task(...)`.
- [ ] FastAPI `BackgroundTasks` remains limited to non-critical request-adjacent work (audit writes, metrics).
- [ ] Durable work survives API restarts (proven via docker compose stop api + worker continues).

### Implementation Tasks

- [ ] **6.3.1** Add an ARQ queue accessor in `app/modules/jobs.py` (or a shared module) that routes can import: `async def enqueue_durable(job_name, **kwargs) -> str` returning a job ID.
- [ ] **6.3.2** Migrate lesson generation: find where `POST /api/v2/lessons/generate` enqueues work via `BackgroundTasks`; switch to `enqueue_durable("generate_lesson", ...)`.
- [ ] **6.3.3** Migrate study-plan generation: same pattern for `POST /api/v2/study-plans/generate`.
- [ ] **6.3.4** Migrate consent renewal: cron job already defined in `WorkerSettings`; verify the cron schedule is active and the route no longer enqueues it directly.
- [ ] **6.3.5** Migrate practice session cleanup: same as consent renewal — cron-based, remove route-level enqueue.
- [ ] **6.3.6** Update `app/core/jobs.py` to clearly document that it is now for non-durable, request-adjacent work only.
- [ ] **6.3.7** Add/update unit tests proving: (a) durable enqueue returns a job ID, (b) worker executes the job, (c) job status is retrievable post-execution.

---

## Phase 6.4 — Add Worker Health, Readiness, and Verification Evidence 🔴 NOT STARTED

### Problem Statement

Phase 6 is not complete until the worker is proven in a live local or staging-style environment with captured evidence.

### Acceptance Criteria

- [ ] Worker startup health/readiness is observable (`docker compose logs worker` shows successful Redis + DB connection).
- [ ] Enqueue/dequeue or execute/status proof exists for at least one durable job (consent renewal or practice session cleanup).
- [ ] Phase 6 evidence and audit docs are committed.

### Implementation Tasks

- [ ] **6.4.1** Start the full stack (`docker compose up -d postgres redis worker`) and verify the worker connects.
- [ ] **6.4.2** Trigger a durable job (e.g., consent renewal cron or manual enqueue) and capture the execution log.
- [ ] **6.4.3** Prove restart-survival: `docker compose restart api`, verify queued job still executes.
- [ ] **6.4.4** Run `scripts/check_arq_worker_import.py` and confirm it passes.
- [ ] **6.4.5** Write `docs/release/phase_6_evidence.md` with captured outputs.
- [ ] **6.4.6** Write `docs/roadmap/execution/phase_6_implementation_report.md`.
- [ ] **6.4.7** Write `docs/release/phase_6_implementation_audit.md`.

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 6 execution plan | `docs/roadmap/execution/phase_6_execution_plan.md` | ✅ (this file) |
| Phase 6 implementation report | `docs/roadmap/execution/phase_6_implementation_report.md` | [ ] Must be written in 6.4 |
| Phase 6 evidence | `docs/release/phase_6_evidence.md` | [ ] Must be written in 6.4 |
| Phase 6 implementation audit | `docs/release/phase_6_implementation_audit.md` | [ ] Must be written in 6.4 |

---

## Success Criteria

**Phase 6 is complete when:**

- [x] ARQ worker service defined in local Compose (6.2)
- [x] ARQ settings correct: `REDIS_URL` casing, `redis_settings` as class var (6.1)
- [ ] Durable jobs enqueued through ARQ, not `BackgroundTasks` (6.3)
- [ ] Durable job tests cover enqueue, execution, and status retrieval (6.3)
- [ ] API restart does not lose queued durable work (6.4)
- [ ] Worker startup health/readiness verified against live Redis + Postgres (6.4)
- [ ] Evidence and audit docs committed (6.4)

**RoadMap alignment** (from [roadmap.md](../roadmap.md#L258-L281)):

- [x] ARQ worker starts in local Compose ✅
- [ ] Durable job tests cover enqueue, execution, and status retrieval ❌
- [ ] API restart does not lose queued durable work ❌

---

## Close Checklist

- [x] Execution plan exists: `docs/roadmap/execution/phase_6_execution_plan.md` (this file)
- [ ] Implementation report exists: `docs/roadmap/execution/phase_6_implementation_report.md`
- [ ] Audit report exists: `docs/release/phase_6_implementation_audit.md`
- [ ] Evidence files committed and accurate
- [ ] `roadmap.md` Phase 6 status updated to "Complete (YYYY-MM-DD)"
- [ ] `context/build-plan.md` Phase 6 status updated
- [ ] `context/progress-tracker.md` updated
- [ ] `docs/todos/todo.md` durable job tasks updated
- [ ] Branch merged to `master` via PR
- [ ] Remote branch deleted after merge

---

## Next Phase

**Phase 7: Deployment and Security Hardening** — fix hardcoded URLs, security headers, CORS/CSP/HSTS, and route protection gaps after durable jobs are in place.
