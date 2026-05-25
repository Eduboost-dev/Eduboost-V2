# Content Factory Refreshed Status

Status: implemented and locally tested on branch `feature/content-factory-refreshed`; CI, staging, educator review, and production promotion are not yet proven.

| Field | Value |
|---|---|
| Captured at | 2026-05-25 |
| Plan source | `temp/EduBoost_Content_Factory_Refreshed_Plan_25-May-2026.md` |
| ETL source assets | `temp/etl/` integrated into `app/services/etl/` |
| Backend API | `/api/v2/content-factory` |
| Admin UI | `/admin/content-factory` |
| Migration | `alembic/versions/20260525_1531_content_factory_etl_integration.py` |
| Local test evidence | `python3 -m pytest tests/unit/test_content_factory_services.py -q --no-cov` -> `4 passed` |
| Frontend evidence | `npm run type-check` in `app/frontend` passed |

## Implemented Scope

- Added app-native Content Factory tables for scopes, coverage targets, generation runs, generation tasks, artifacts, artifact-source links, validation reports, review actions, seed runs, promotion events, lesson bank, assessment blueprints, and study-plan templates.
- Integrated the refreshed ETL pipeline files and MCP wrappers under `app/services/etl/` so the plan assets are now part of the codebase rather than temporary files.
- Added provenance validation that requires generated artifacts to cite approved, indexed, or training-ready ETL sources before they can enter review.
- Added deterministic validation for diagnostic artifacts, including answer-key presence and source traceability checks.
- Added admin-only API routes to validate source bundles, create artifacts, revalidate artifacts, fetch artifacts, and record review decisions.
- Added a Next.js admin entry point for the ETL/Content Factory dashboard at `/admin/content-factory`.
- Added unit tests for the source approval gate, source snapshot hashing, diagnostic answer-key validation, and API router registration.

## Current Project State Impact

This branch moves the Content Factory from a plan/temp-asset state to a repository-side implementation foundation. It does not yet prove full generation throughput, educator approval, staging promotion, production seeding, or CI authority.

## Remaining Work

- Run Alembic upgrade/downgrade against a disposable PostgreSQL database and capture runtime migration evidence.
- Add CI coverage for the Content Factory validation tests and frontend admin type-check path.
- Replace or extend the imported dashboard mock data with live calls to `/api/v2/content-factory` once operator workflows are finalized.
- Add educator review workflow evidence before generated content is treated as externally approved.
- Add staging seed and rollback evidence before promoting generated artifacts into learner-facing production tables.
