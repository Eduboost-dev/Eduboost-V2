# Phase 6 Evidence — Durable Background Jobs

**Date**: 2026-06-11
**Status**: CODE COMPLETE — Live Docker verification pending (see `scripts/verify_phase6_live.sh`)
**Branch**: `phase-6/durable-background-jobs`

---

## Static Verification

### Compilation Check

```
$ python -m compileall -q app/modules/jobs.py app/core/jobs.py app/jobs/consent_renewal_job.py app/jobs/practice_session_cleanup_job.py app/api_v2_routers/lessons.py app/api_v2_routers/study_plans.py app/api_v2_routers/consent_renewal.py
Exit: 0
```

All Phase 6 files compile cleanly.

### ARQ Worker Import Check

`scripts/check_arq_worker_import.py` exists and can be executed against a working environment.

---

## Code Changes Evidence

### 6.1 — ARQ Settings Fix

**Before**: `WorkerSettings.redis_settings` was a `@classmethod` accessing `cfg.redis_url` (lowercase).
**After**: `redis_settings` is a class variable accessing `cfg.REDIS_URL` (uppercase).

Commit `dad8c5e7` — `feat: wire arq worker into compose`

```diff
-    @classmethod
-    def redis_settings(cls) -> RedisSettings:
-        cfg = get_settings()
-        import urllib.parse
-        parsed = urllib.parse.urlparse(cfg.redis_url)
-        return RedisSettings(...)
+    cfg = get_settings()
+    parsed_redis_url = urlparse(cfg.REDIS_URL)
+    redis_settings = RedisSettings(...)
```

### 6.2 — Compose Wiring

**docker-compose.yml** (+26 lines):
- Worker service with `Dockerfile.v2`, command `arq app.modules.jobs.WorkerSettings`
- Environment: `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`
- Dependencies: postgres + redis (health-check gated)

**docker-compose.prod.yml** (+29 lines):
- Same structure with production environment
- Additional secrets: `ENCRYPTION_KEY`, `ENCRYPTION_SALT`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`

### 6.3 — BackgroundTasks Migration

Three critical routes migrated from `background_tasks.add_task(...)` to `enqueue_durable(...)`:

| Route | From | To |
|-------|------|----|
| `POST /api/v2/lessons/generate` | `background_tasks.add_task(run_job, ...)` | `enqueue_durable("generate_lesson_job", ...)` |
| `POST /api/v2/study-plans/{id}` | `background_tasks.add_task(run_job, ...)` | `enqueue_durable("generate_study_plan_job", ...)` |
| `POST /api/v2/admin/consent/renew` | N/A (new route) | `enqueue_durable("send_consent_renewal_reminders", ...)` |

Two request-adjacent routes correctly remain on `BackgroundTasks`:
- `DELETE /api/v2/learners/{id}` — `enqueue_data_purge` (POPIA data purge — durable-optional)
- `POST /api/v2/parents/purge` — `_log_purge_request` (audit logging — request-adjacent-ok)

### 6.4 — Unit Tests

`tests/unit/test_phase6_durable_jobs.py` — 171 lines, 5 test functions

| Test | What It Proves |
|------|---------------|
| `test_enqueue_durable_returns_job_id_and_calls_arq_pool` | enqueue → job ID returned → ARQ pool.enqueue_job called |
| `test_generate_lesson_job_updates_status_and_result` | lesson job executes → status "completed" → result stored |
| `test_generate_study_plan_job_updates_status_and_result` | study plan job executes → status "completed" → result stored |
| `test_consent_renewal_job_updates_status_and_result` | consent renewal → status "completed" → result stored |
| `test_consent_renewal_job_ignores_runtime_objects_in_ctx` | runtime objects in ctx don't break job execution |

Integration tests in `tests/integration/test_v2_jobs.py` cover route-level behavior with mocked `enqueue_durable`.

---

## WorkerSettings Verification

The `WorkerSettings` class in `app/modules/jobs.py` registers:

**functions**: `send_consent_reminders`, `send_consent_renewal_reminders`, `generate_lesson_job`, `generate_study_plan_job`, `run_practice_session_cleanup`, `process_rlhf_feedback_batch`, `expire_stale_diagnostic_sessions`, `run_database_backup`

**cron_jobs**:
- Daily 00:00 UTC — `run_database_backup`
- Daily 06:00 UTC — `send_consent_renewal_reminders`
- Daily 01:00 UTC — `run_practice_session_cleanup`
- Hourly — `expire_stale_diagnostic_sessions`

---

## Limitations

- Live Docker Compose verification not performed (venv broken, no Docker in session).
- Unit tests not executed (venv has zero-byte Python). Syntax validated via `compileall`.
- **Verification script available**: `scripts/verify_phase6_live.sh` documents the procedure to close the remaining gaps once Docker is available.