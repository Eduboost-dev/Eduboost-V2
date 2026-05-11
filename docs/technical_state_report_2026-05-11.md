# EduBoost V2 Technical State Report

Date: 2026-05-11
Branch assessed: `codex/cluster-c-popia-consent-audi`
Base commit assessed: `cc4140f docs: add production readiness roadmap`

## Executive Summary

EduBoost V2 is a substantial production-readiness implementation, but it is not
public-beta-ready or production-ready. The backend runtime, OpenAPI generation,
smoke tests, diagnostics assessment checks, and documentation-contract checks
have green local evidence on the assessed base branch. The broader system still
has real release blockers in consent coverage, staging evidence, migration
execution, frontend/browser validation, legal approval, item-bank approval, and
release evidence packaging.

The most important recent improvement is process discipline: the project now
has a production-readiness roadmap, a current-state source of truth, and a
separate PR branch train from PR1 through PR16 that adds reviewable evidence
gates for each roadmap batch. Those PR branches are not merged into the base
branch yet, so this report separates "base branch truth" from "pending PR
branch evidence".

## Current Base Branch Truth

The base branch contains:

- FastAPI V2 runtime: `app.api_v2:app`.
- Legacy compatibility shim: `app.legacy.api.main:app`.
- V2 routers mounted under `/api/v2` and `/v2`.
- Operational routes: `/`, `/health`, `/ready`, `/metrics`,
  `/v2/health/deep`, `/docs`, `/redoc`, and `/openapi.json`.
- OpenAPI generation and drift checking.
- Route inventory and PR-002R evidence scaffolding.
- POPIA, consent, data-rights, audit, authorization, diagnostics, AI safety,
  frontend, data-resilience, and operations evidence documents.
- Grade 4 Mathematics item-bank work with 14 approved starter items plus
  generated candidate content that still needs approval before production CAPS
  coverage can be claimed.

Base `TODO.md` status at assessment time:

- Checked `[x]`: 12
- Verification `[verify]`: 13
- Open `[ ]`: 1424
- Python test files under `tests`: 423

The low `[verify]` count on the base branch is expected because PR7-PR16 TODO
updates live on their respective PR branches and have not been merged.

## Verified On Base Branch

These commands passed locally on 2026-05-11:

```bash
make runtime-check
make openapi-check
make beta-release-readiness-contract-check
pytest tests/smoke tests/test_entrypoints.py tests/test_health_checks.py -q --no-cov
make diagnostics-assessment-check
```

Observed results:

- Runtime entrypoint check passed for `app.api_v2:app` and
  `app.legacy.api.main:app`.
- OpenAPI drift check passed.
- Beta-release readiness contract check passed as a documentation-contract
  check only.
- Smoke/entrypoint/health suite passed with 35 passed and 4 skipped.
- Diagnostics assessment suite passed with 12 tests passed.

## Failed Or Not Yet Verified On Base Branch

### Consent-Gate Coverage

`make popia-consent-gate-check` failed.

Observed result:

- Missing consent markers: 207
- Baseline allowlist entries: 104
- New unallowlisted missing markers: 103

The missing-marker list includes diagnostic session functions, IRT functions,
item-bank functions, lesson generation/validation functions, progress/mastery
functions, and study-plan updater functions. Some of these may be internal
helpers that should be allowlisted; others likely need explicit consent-gate
evidence. This is a real blocker for privacy-readiness claims.

### Migration/Schema Make Target

`make migration-check` failed on the base branch because
`scripts/validate_schema_integrity.py` cannot import `app` when invoked
directly:

```text
ModuleNotFoundError: No module named 'app'
```

This is a script portability issue on the base branch. The fix exists in PR4
(`codex/pr4-persistence-resilience`) but is not merged into the assessed base
branch.

### Release-Relevant Evidence Still Missing

The following remain unverified as release-ready:

- Staging deployment.
- Staging smoke evidence.
- Browser Playwright run against staging.
- Frontend install/test/build evidence on the assessed commit.
- Disposable PostgreSQL migration run.
- Backup/restore drill in a separate environment.
- Redis outage/recoverability exercise.
- Production CORS/security-header verification.
- Legal review and approval of public-facing policies.
- Full POPIA negative-path and data-rights execution evidence.
- Full item-bank production approval for claimed CAPS scope.
- Live LLM provider safety evidence.
- Billing/email provider readiness or explicit beta exclusion.
- Release evidence bundle, rollback test, and go/no-go record.

## Pending PR Branch Train

Sixteen PR branches were created from the current base. They add focused,
reviewable evidence gates and TODO updates for the production-readiness roadmap.

| PR | Branch | Latest commit | Scope |
| --- | --- | --- | --- |
| 1 | `codex/pr1-repo-truth` | `1c59a27` | Repository governance and repo-state verification |
| 2 | `codex/pr2-runtime-contract` | `fdd0427` | Runtime contract, router registration, legacy exclusion, route inventory, OpenAPI |
| 3 | `codex/pr3-privacy-boundary` | `b3ad1f8` | Privacy-boundary evidence gate |
| 4 | `codex/pr4-persistence-resilience` | `0a57877` | Persistence evidence gate and schema-integrity import fix |
| 5 | `codex/pr5-learning-evidence` | `bb2677a` | Learning evidence gate |
| 6 | `codex/pr6-api-envelope-error-contract` | `06bf879` | API envelope and error-contract evidence |
| 7 | `codex/pr7-auth-boundary` | `5261640` | Auth/token/cookie/RBAC/object-auth evidence |
| 8 | `codex/pr8-popia-legal` | `cec4e10` | POPIA/legal evidence |
| 9 | `codex/pr9-db-repositories` | `bbce980` | DB/repository evidence |
| 10 | `codex/pr10-backup-redis-dr` | `77eefc0` | Backup/Redis/DR evidence |
| 11 | `codex/pr11-ai-safety` | `1c385ff` | AI safety release evidence |
| 12 | `codex/pr12-caps-learning-proof` | `f3ba366` | CAPS/learning proof |
| 13 | `codex/pr13-frontend-journeys` | `4820832` | Frontend journey evidence |
| 14 | `codex/pr14-accessibility-pwa-e2e` | `439110c` | Accessibility/PWA/E2E evidence |
| 15 | `codex/pr15-cicd-staging` | `533c666` | CI/CD and staging evidence |
| 16 | `codex/pr16-observability-ops` | `430d8f5` | Observability/ops evidence |

These branches are useful because they make each work batch independently
reviewable. They are not equivalent to release readiness. Many of the checks are
evidence-presence gates, not live environment validations.

## Architecture Assessment

### Backend

The backend is a modular FastAPI application with a clear V2 runtime and a broad
router surface. It includes operational routes, metrics, readiness checks,
authorization helpers, POPIA/data-rights routes, diagnostics, lessons, billing,
jobs, and system routes.

Strengths:

- Canonical runtime is importable.
- OpenAPI generation is automated and drift-checked.
- Global exception envelope and API envelope helpers exist.
- Object-authorization and consent evidence scaffolding is substantial.
- Metrics and health endpoints are present.

Risks:

- Base branch legacy shim still reports one additional route compared with the
  canonical app during runtime check. PR2 fixes the non-mutating compatibility
  behavior, but that fix is not merged.
- Consent-gate inventory has unresolved gaps.
- Not every router has success-envelope proof.
- Security and auth abuse-path coverage is not yet complete.

### Data And Persistence

The repository contains migration graph checks, schema integrity scripts,
repository pattern tests, backup/restore scripts, and data-resilience evidence.

Strengths:

- Migration and schema validation tooling exists.
- Backup/restore command scaffolds and integrity check scripts exist.
- Data-resilience evidence documents are extensive.

Risks:

- Base `make migration-check` currently fails due to import-path setup.
- Migration smoke against disposable PostgreSQL is still not verified on the
  assessed commit.
- Transaction rollback and repository behavior are not yet proven for every
  sensitive workflow.
- Backup/restore evidence is not a substitute for a real staged restore.

### Privacy, Security, And POPIA

The privacy/compliance surface is broad and unusually well documented for this
stage. There are POPIA routes, consent services, audit contracts, data-rights
docs, retention docs, and authorization evidence.

Strengths:

- POPIA/data-rights and audit evidence exist.
- Object-authorization wiring has extensive test/doc coverage.
- Consent/audit closure documents and checks exist.

Risks:

- Consent-gate check fails on the base branch.
- Legal documents still require external legal review and approval.
- Branch-protection evidence is still external to the repo.
- Staging proof for data-rights workflows is still missing.

### AI, CAPS, Diagnostics, And Mastery

The project has meaningful implementation in diagnostics, IRT, item bank,
practice, spaced repetition, mastery, learning velocity, CAPS alignment, and AI
safety contracts.

Strengths:

- `make diagnostics-assessment-check` passes.
- IRT hardening, session lifecycle, mastery, and practice tests pass.
- AI safety, prompt, output-schema, refusal, and provider-fallback evidence
  exists.
- CAPS/item-bank documentation correctly states that approval remains open.

Risks:

- Full CAPS coverage is not approved.
- Only 14 Grade 4 Mathematics starter items are approved.
- Generated candidate items cannot support production claims until reviewed and
  promoted.
- Live LLM provider behavior and educator review remain release blockers.

### Frontend

The frontend is a Next.js application with API client code, learner and parent
journey components, route guards, accessibility helpers, service worker, offline
sync, frontend tests, fixtures, and Playwright scaffolding.

Strengths:

- API client and fixture evidence exists.
- Learner/parent journey contracts exist.
- Accessibility and PWA/offline assets exist.
- Playwright specs and mocked journey scaffolding exist.

Risks:

- Frontend install/test/build was not rerun in this assessment.
- Browser E2E against staging is not verified.
- Real-device/mobile accessibility evidence is not present.

### Operations

The repo contains Prometheus/Grafana/Alertmanager assets, metrics code,
deployment runbooks, staging gate docs, incident response docs, support model,
and beta monitoring/support evidence.

Strengths:

- Operational assets are present and testable.
- Metrics endpoint exists and is covered by smoke/health tests.
- CI/CD and staging documents exist.

Risks:

- Staging deployment is not proven.
- Alert firing and dashboard screenshots are missing.
- Incident tabletop exercise evidence is missing.
- Release evidence bundle and rollback proof are still absent.

## Overall Readiness Rating

Current status: production-readiness implementation, not public-beta-ready.

Approximate readiness by area:

| Area | State |
| --- | --- |
| Backend runtime/API baseline | Mostly implemented; base checks pass, PR2 has important cleanup |
| API envelope/error contract | Implemented; full router rollout incomplete |
| Auth/object authorization | Substantial evidence; abuse-path coverage incomplete |
| POPIA/consent/audit | Strong docs and scaffolding; consent-gate check failing |
| Data/migrations/backup | Tooling exists; base migration-check failing; live DB evidence missing |
| AI/CAPS/diagnostics | Good implementation; item-bank approval and live AI evidence missing |
| Frontend | Implemented and documented; fresh build/E2E evidence missing |
| CI/CD/staging | Workflows/docs exist; live staging deployment missing |
| Observability/ops | Assets exist; live alert/dashboard/tabletop evidence missing |
| Release governance | Roadmap and evidence gates exist; go/no-go package missing |

## Recommended Next Actions

1. Review and merge PR1 through PR6 first. They establish repo truth, runtime
   contract, privacy evidence structure, persistence evidence structure,
   learning evidence structure, and API envelope/error contract evidence.
2. Merge PR7 through PR16 only after confirming the team accepts evidence gates
   as incremental review artifacts, not release-complete claims.
3. Fix or classify the 103 new consent-gate findings. This is the highest-risk
   blocker currently visible from automated checks.
4. Merge the PR4 schema-integrity import fix or apply it directly, then rerun
   `make migration-check`.
5. Run frontend `npm` install/test/build from `app/frontend` and record exact
   output.
6. Run migrations against a disposable PostgreSQL database and record evidence.
7. Run backup and restore dry-runs in a separate environment.
8. Decide beta scope for billing and notifications: either verify them or
   explicitly exclude them.
9. Promote only human-reviewed item-bank content into production claims.
10. Build the final release evidence bundle only after staging, rollback,
    legal, privacy, and operational checks have green evidence.

## Bottom Line

The system is moving in the right direction and now has a disciplined evidence
model. The core runtime and diagnostics checks are green, and the PR branch
train gives the project a reviewable path through the production-readiness
roadmap. The project should still be described as an implementation under
production hardening, not a beta-ready platform. The most urgent technical
blockers are consent-gate reconciliation, migration-check portability on the
base branch, and fresh environment-backed evidence for frontend, database,
backup/restore, staging, legal, and operations.

