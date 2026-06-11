# Phase 6 Implementation Report

**Date**: 2026-06-11
**Branch**: `phase-6/durable-background-jobs`
**Status**: In progress

## Summary

Phase 6 now has durable ARQ wiring for the API jobs that were still running through request-scoped `BackgroundTasks`. The API routes for lesson generation, study-plan generation, and consent renewal now enqueue durable jobs, the worker registry includes the durable jobs required by the plan, and the worker contract checks pass.

The only remaining gap is live Docker-based verification. The code for worker startup health checks is in place, but the local Docker daemon was not responsive from this session, so the compose-based evidence could not be captured.

## Before

| Area | Before |
|---|---|
| Lesson generation | `POST /v2/lessons/generate` used `BackgroundTasks` and in-process job state |
| Study-plan generation | `POST /v2/study-plans/generate/{learner_id}` used `BackgroundTasks` |
| Consent renewal | Admin trigger route used `BackgroundTasks` and in-process job state |
| Worker registry | ARQ worker settings existed, but did not include the new durable lesson/study-plan jobs |
| Worker status tracking | Job status remained tied to the request-scoped helper instead of durable job ids |
| Worker readiness | No explicit startup DB/Redis readiness verification was logged |

## After

| Area | After |
|---|---|
| Durable enqueue helper | Added `enqueue_durable(...)` in `app/modules/jobs.py` to create the shared job record and enqueue the ARQ job |
| Lesson generation | Route now enqueues `generate_lesson_job` on ARQ |
| Study-plan generation | Route now enqueues `generate_study_plan_job` on ARQ |
| Consent renewal | Admin route now enqueues `send_consent_renewal_reminders` on ARQ |
| Practice cleanup | Worker registry now includes `run_practice_session_cleanup` on the cron schedule |
| Worker status tracking | Worker functions update the shared job record to `running`, `completed`, or `failed` |
| Worker readiness | Worker startup now checks DB and Redis readiness before logging startup success |

## Current Code Changes

| File | Change |
|---|---|
| `app/modules/jobs.py` | Added durable enqueue helper, lesson/study-plan jobs, status updates, and startup readiness checks |
| `app/api_v2_routers/lessons.py` | Switched lesson generation to durable enqueueing |
| `app/api_v2_routers/study_plans.py` | Switched study-plan generation to durable enqueueing |
| `app/api_v2_routers/consent_renewal.py` | Switched consent renewal to durable enqueueing |
| `app/jobs/consent_renewal_job.py` | Added durable status updates and worker-context fallback handling |
| `app/jobs/practice_session_cleanup_job.py` | Added durable status updates and worker-context fallback handling |
| `app/core/jobs.py` | Clarified that the module is request-adjacent only |
| `scripts/check_arq_worker_import.py` | Extended worker contract checks to cover the new durable jobs |
| `tests/unit/test_phase6_durable_jobs.py` | Added enqueue/execution/status tests |
| `tests/integration/test_v2_jobs.py` | Updated route tests for durable enqueueing |

## Evidence

- `python3 scripts/check_arq_worker_import.py` passed.
- `pytest -q tests/unit/test_arq_worker_import_contract.py tests/unit/test_phase6_durable_jobs.py tests/integration/test_v2_jobs.py --no-cov` passed with `9 passed, 3 skipped`.
- `python3 -m compileall` passed on the touched Python files.

## Open Gap

The Phase 6.4 live Docker verification step is still blocked in this environment because the Docker daemon was not responsive from WSL. The code change for readiness checks is present, but the runtime evidence must be captured from a working Docker environment before Phase 6 can be closed.
