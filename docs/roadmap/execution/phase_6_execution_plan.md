# Phase 6 Execution Plan — Durable Background Jobs

**Date**: 2026-06-10
**Status**: IN PROGRESS
**Branch**: `phase-6/durable-background-jobs`
**Scope**: Replace request-adjacent placeholder job handling with durable ARQ worker wiring, compose/production deployment support, and verification evidence.
**Priority**: P1 (per [roadmap.md](../roadmap.md#L258-L281))

---

## Pre-Conditions

Before Phase 6 implementation begins:

- [ ] Confirm the local repo is still on the Phase 5 branch or create the Phase 6 branch before making code changes.
- [ ] Confirm Redis is available for worker/runtime verification.
- [ ] Confirm Docker Compose definitions are the current deployment source of truth for local worker wiring.

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

## Phase 6.1 — Fix ARQ Settings and Worker Wiring

### Problem Statement

The codebase already has ARQ job definitions, but the deployment/runtime path is not fully authoritative. The roadmap flags likely settings casing issues and missing worker deployment.

### Acceptance Criteria

- [ ] ARQ settings resolve correctly for worker startup and runtime configuration.
- [ ] ARQ worker entrypoint runs with the expected `WorkerSettings`.
- [ ] The worker job set includes the durable jobs required by the roadmap.

### Implementation Tasks

- [ ] Inspect and correct ARQ settings references across worker/config files.
- [ ] Verify the worker entrypoint and `WorkerSettings` import paths are stable.
- [ ] Confirm cron jobs and on-demand jobs are registered with the intended names.
- [ ] Update any import-compat fallback docs or comments that are now misleading.

---

## Phase 6.2 — Wire the Durable Worker into Compose / Production

### Problem Statement

The worker logic exists in code, but the deployment stack still needs an explicit service definition and startup path.

### Acceptance Criteria

- [ ] Local Compose starts the ARQ worker successfully.
- [ ] Production Compose / deployment manifests include the worker.
- [ ] Redis connectivity is available to the worker in local and production-like environments.

### Implementation Tasks

- [ ] Add or fix an ARQ worker service in `docker-compose.yml`.
- [ ] Mirror the worker service in `docker-compose.prod.yml` if production uses Compose.
- [ ] Ensure the worker container uses the same settings source as the API container.
- [ ] Add or update a worker Dockerfile if the current runtime requires one.

---

## Phase 6.3 — Move Durable Work Off Request-Adjacent BackgroundTasks

### Problem Statement

The roadmap requires durable jobs rather than request-scoped `BackgroundTasks` for long-running or restart-sensitive work.

### Acceptance Criteria

- [ ] Durable jobs are enqueued through ARQ or an equivalent durable worker path.
- [ ] FastAPI `BackgroundTasks` remains limited to non-critical request-adjacent work.
- [ ] Durable work survives API restarts.

### Implementation Tasks

- [ ] Review routes that currently return job IDs and identify which ones must be switched to durable enqueueing.
- [ ] Move consent renewal, lesson generation, study-plan generation, and any other durable flows onto the worker path where appropriate.
- [ ] Keep request-adjacent work in `app/core/jobs.py` only if it is truly non-critical and short-lived.
- [ ] Update route/service docs to describe the durable path clearly.

---

## Phase 6.4 — Add Worker Health, Readiness, and Verification Evidence

### Problem Statement

Phase 6 is not complete until the worker is proven in a live local or staging-style environment.

### Acceptance Criteria

- [ ] Worker startup health/readiness is observable.
- [ ] Enqueue/dequeue or execute/status proof exists for at least one durable job.
- [ ] Phase 6 evidence is captured in `docs/release/`.

### Implementation Tasks

- [ ] Add or update health checks for worker / Redis connectivity.
- [ ] Run the worker locally and capture a successful job execution proof.
- [ ] Add or update tests that cover worker import, registration, and job execution behavior.
- [ ] Write the Phase 6 evidence and implementation audit docs after verification.

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 6 implementation report | `docs/roadmap/execution/phase_6_implementation_report.md` | [ ] |
| Phase 6 evidence | `docs/release/phase_6_evidence.md` | [ ] |
| Phase 6 implementation audit | `docs/release/phase_6_implementation_audit.md` | [ ] |

---

## Success Criteria

**Phase 6 is complete when:**

- [ ] ARQ worker starts in local Compose
- [ ] Durable job tests cover enqueue, execution, and status retrieval
- [ ] API restart does not lose queued durable work
- [ ] FastAPI `BackgroundTasks` is no longer the durable job mechanism
- [ ] Evidence and audit docs are committed

---

## Close Checklist

- [ ] Execution plan exists: `docs/roadmap/execution/phase_6_execution_plan.md` (this file)
- [ ] Implementation report exists: `docs/roadmap/execution/phase_6_implementation_report.md`
- [ ] Audit report exists: `docs/release/phase_6_implementation_audit.md`
- [ ] Evidence files committed and accurate
- [ ] `roadmap.md` Phase 6 status updated to "In progress" or "Complete (YYYY-MM-DD)" when appropriate
- [ ] `context/build-plan.md` Phase 6 status updated
- [ ] `context/progress-tracker.md` updated
- [ ] `docs/todos/todo.md` durable job tasks updated

---

## Next Phase

**Phase 7: Deployment and Security Hardening** — fix hardcoded URLs, security headers, and route protection gaps after durable jobs are in place.
