# Phase 6 Implementation Audit

**Date**: 2026-06-11
**Branch**: `phase-6/durable-background-jobs`

## Audit Result

**Status**: Partial pass, blocked on live Docker verification

## Acceptance Criteria Review

### 6.1 ARQ settings and worker wiring

- [x] ARQ settings resolve correctly for worker startup and runtime configuration.
- [x] ARQ worker entrypoint runs with the expected `WorkerSettings`.
- [x] The worker job set includes the durable jobs required by the roadmap.

Evidence:

- `scripts/check_arq_worker_import.py` passes.
- `app/modules/jobs.py` now exposes `generate_lesson_job`, `generate_study_plan_job`, `send_consent_renewal_reminders`, and `run_practice_session_cleanup`.

### 6.2 Compose / production wiring

- [x] Local Compose defines the ARQ worker service.
- [x] Production Compose defines the ARQ worker service.
- [x] Redis connectivity is configured for the worker in both compose files.

Evidence:

- `docker-compose.yml` and `docker-compose.prod.yml` both define `worker`.

### 6.3 Durable jobs off `BackgroundTasks`

- [x] Durable jobs are enqueued through ARQ rather than `BackgroundTasks`.
- [x] FastAPI `BackgroundTasks` remains limited to request-adjacent work.
- [x] The durable route paths were updated for lesson generation, study-plan generation, and consent renewal.
- [x] Practice-session cleanup is now worker-backed through the ARQ registry and cron schedule.

Evidence:

- `app/api_v2_routers/lessons.py`
- `app/api_v2_routers/study_plans.py`
- `app/api_v2_routers/consent_renewal.py`
- `app/core/jobs.py`

### 6.4 Worker health, readiness, and verification evidence

- [ ] Worker startup health/readiness is observable in a live Docker environment.
- [ ] Enqueue/dequeue or execute/status proof exists for at least one durable job.
- [ ] Phase 6 evidence and audit docs are committed.

Evidence:

- Worker startup readiness checks are implemented in `app/modules/jobs.py`.
- The live Docker verification step could not be completed in this session because the Docker daemon was not responsive from WSL.

## Test Evidence

- `python3 scripts/check_arq_worker_import.py`
- `pytest -q tests/unit/test_arq_worker_import_contract.py tests/unit/test_phase6_durable_jobs.py tests/integration/test_v2_jobs.py --no-cov`
- `python3 -m compileall` on the touched Python files

## Conclusion

Phase 6 is substantially implemented, but the plan is not fully closed because the live Docker verification requested by 6.4 could not be completed in this environment.
