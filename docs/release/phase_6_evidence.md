# Phase 6 Evidence

**Date**: 2026-06-11
**Branch**: `phase-6/durable-background-jobs`

## Verified Outputs

### ARQ worker import contract

Command:

```bash
python3 scripts/check_arq_worker_import.py
```

Result:

```text
ARQ dependency and worker import check
- PASS arq pinned in: requirements/base.in, requirements/base.txt, requirements.txt, requirements-dev.txt, requirements/dev.in, requirements/dev.txt
- PASS imported app.modules.jobs
- PASS arq compat imports; available=False
- PASS worker exposes send_consent_reminders
- PASS worker exposes send_consent_renewal_reminders
- PASS worker exposes generate_lesson_job
- PASS worker exposes generate_study_plan_job
- PASS worker exposes run_practice_session_cleanup
- PASS jobs.py delegates consent reminder dependencies to job_dependency_factory
- PASS syntax app/services/arq_import_compat.py
- PASS syntax app/services/job_dependency_factory.py
- PASS syntax app/modules/jobs.py
- PASS syntax scripts/repair_arq_dependency_worker_import.py
- PASS syntax scripts/check_arq_worker_import.py
- PASS syntax tests/unit/test_arq_worker_import_contract.py
- PASS ARQ worker import contract tests
- PASS focused ruff ARQ worker check
- PASS ARQ dependency and worker import check
```

### Targeted test run

Command:

```bash
pytest -q tests/unit/test_arq_worker_import_contract.py tests/unit/test_phase6_durable_jobs.py tests/integration/test_v2_jobs.py --no-cov
```

Result:

```text
9 passed, 3 skipped in 8.44s
```

### Compile check

Command:

```bash
python3 -m compileall -q app/modules/jobs.py app/jobs/consent_renewal_job.py app/jobs/practice_session_cleanup_job.py app/api_v2_routers/lessons.py app/api_v2_routers/study_plans.py app/api_v2_routers/consent_renewal.py app/core/jobs.py app/services/consent_renewal_service.py scripts/check_arq_worker_import.py tests/unit/test_arq_worker_import_contract.py tests/unit/test_phase6_durable_jobs.py tests/integration/test_v2_jobs.py
```

Result:

```text
PASS
```

## Live Stack Attempt

I attempted to start the local worker stack with Docker Compose using the dev services (`postgres`, `redis`, `worker`). The compose parser required `GRAFANA_ADMIN_PASSWORD`, which was then supplied. After that, the Docker/WSL path became unresponsive in this environment and the live stack could not be verified.

Observed blockers:

- `docker compose up -d postgres redis worker` timed out
- follow-up `docker compose ps` and `docker compose logs worker` calls also timed out
- `docker ps` timed out as well, suggesting the Docker daemon was not reachable from this session

## Notes

- The code path for durable enqueueing, worker execution, and job-status persistence is implemented and unit-tested.
- The remaining Phase 6.4 live verification step needs a responsive Docker daemon or an alternate runtime environment.
