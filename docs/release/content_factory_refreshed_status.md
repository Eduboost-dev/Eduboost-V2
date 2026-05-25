# Content Factory Refreshed Status

Status: implemented and locally tested on branch `feature/content-factory-refreshed`; CI, staging, educator review, and production promotion are not yet proven.

| Field | Value |
|---|---|
| Captured at | 2026-05-25 |
| Plan source | `temp/EduBoost_Content_Factory_Refreshed_Plan_25-May-2026.md` |
| ETL source assets | `temp/etl/` integrated into `app/services/etl/` |
| Backend API | `/api/v2/admin/content-factory` |
| Admin UI | `/admin/content-factory` |
| Migration | `alembic/versions/20260525_1531_content_factory_etl_integration.py` |
| Local test evidence | `python3 -m pytest tests/unit/test_content_factory_services.py tests/api/test_content_factory_admin_routes.py tests/unit/test_api_v2_router_contract.py -q --no-cov` -> `13 passed` |
| OpenAPI evidence | `python3 scripts/generate_openapi.py && make openapi-check` passed |
| Frontend evidence | `npm run type-check` in `app/frontend` passed |

## Implemented Scope

- Added app-native Content Factory tables for scopes, coverage targets, generation runs, generation tasks, artifacts, artifact-source links, validation reports, review actions, seed runs, promotion events, lesson bank, assessment blueprints, and study-plan templates.
- Integrated the refreshed ETL pipeline files under `app/services/etl/` and isolated optional MCP wrappers under `tools/etl/` so app startup does not require MCP runtime dependencies.
- Added provenance validation that requires generated artifacts to cite approved, indexed, or training-ready ETL sources before they can enter review.
- Added deterministic validation for diagnostic artifacts, including answer-key presence and source traceability checks.
- Added admin-only API routes for health, ETL status, artifact payload validation, and artifact provenance lookup.
- Added a Next.js admin entry point for the ETL/Content Factory dashboard at `/admin/content-factory`.
- Added unit tests for the source approval gate, source snapshot hashing, diagnostic answer-key validation, and API router registration.
- Added API route tests for unauthenticated, non-admin, and admin access plus OpenAPI tag/path inclusion.

## Current Project State Impact

This branch moves the Content Factory from a plan/temp-asset state to a repository-side implementation foundation. It does not yet prove full generation throughput, educator approval, staging promotion, production seeding, or CI authority.

## Remaining Work

- Run Alembic upgrade/downgrade against a disposable PostgreSQL database and capture runtime migration evidence.
- Add CI coverage for the Content Factory validation, admin API, OpenAPI, and frontend admin type-check path.
- Convert `ETLAdminDashboard` from a mock/internal shell into typed live API components before production exposure.
- Replace or extend the imported dashboard mock data with live calls to `/api/v2/admin/content-factory` once operator workflows are finalized.
- Add educator review workflow evidence before generated content is treated as externally approved.
- Add staging seed and rollback evidence before promoting generated artifacts into learner-facing production tables.
