# EduBoost V2 Remediation Roadmap

Date: 2026-06-02

Source audit: [docs/release/eduboost-v2-technical-audit-2026-06-02.md](../release/eduboost-v2-technical-audit-2026-06-02.md)

## Objective

Bring the project from "substantial but not production-ready" to a release-candidate state by fixing verified implementation gaps, aligning runtime and deployment assumptions, and replacing documentation-only confidence with executable checks.

## Guiding Rules

- Treat executable checks as the source of truth.
- Keep fixes scoped and mergeable.
- Make release-blocking failures visible in CI.
- Prefer durable, migrated, observable production behavior over request-local or startup-repair behavior.
- Keep public routes explicit and intentional.

## Phase 0 - Branch, Evidence, and Audit Artifacts

Status: in progress

Deliverables:

- Add the technical audit report to the repository.
- Add this roadmap to the repository.
- Create an implementation branch from the clean `master` state.
- Keep a running implementation log in commits and verification notes.

Acceptance checks:

- `git status` is clean before implementation begins.
- [docs/roadmap/RoadMap.md](../roadmap/RoadMap.md) and [docs/release/eduboost-v2-technical-audit-2026-06-02.md](../release/eduboost-v2-technical-audit-2026-06-02.md) are present in the repository.

## Phase 1 - Release-Blocking Correctness Fixes

Priority: P0

### 1.1 Fix Python Syntax and Compile Gates

Problems addressed:

- `python -m compileall -q app scripts` fails.
- `scripts/maintenance/audit_todo_backlog.py` contains an invalid f-string expression.

Actions:

- Fix the invalid f-string escaping in `scripts/maintenance/audit_todo_backlog.py`.
- Run `python -m compileall -q app scripts`.
- Add or tighten CI so compile checks run for `app` and `scripts`.

Acceptance checks:

- `python -m compileall -q app scripts` passes.
- CI contains a compile gate for backend source and scripts.

### 1.2 Treat Undefined Names as Release-Blocking

Problems addressed:

- Full Ruff found 861 findings.
- At least one `F821 Undefined name` exists in `app/services/etl/etl_pipeline_v2.py`.
- Current CI Ruff gate is too narrow to represent source health.

Actions:

- Fix all `F821` findings.
- Ensure CI blocks on at least `E9,F63,F7,F82,F821`.
- Separate broader style cleanup from correctness gates if needed.

Acceptance checks:

- `ruff check app tests scripts --select E9,F63,F7,F82,F821` passes.
- CI has the same release-blocking correctness gate.

## Phase 2 - Practice Session Security and Durability

Priority: P0

### 2.1 Authenticate Practice Session Continuation Routes

Problems addressed:

- `next-item` and `respond` routes are unauthenticated.
- Session IDs are not bound to current user identity.
- Consent is checked when a session starts, but not when it is continued.

Actions:

- Require authenticated user dependencies on practice session continuation routes.
- Bind in-memory session records to learner/user identity at creation time.
- Reject continuation requests from any other user.
- Re-check learner write/access authorization and active consent on continuation and response.
- Add tests for unauthorized, wrong-user, and consent-denied flows.

Acceptance checks:

- Route introspection shows practice continuation routes have auth dependencies.
- Tests prove a second user cannot read or advance another learner's session.
- Tests prove missing/expired consent blocks continuation.

### 2.2 Replace In-Memory Practice Session State

Problems addressed:

- `_SESSIONS` is process-local.
- Sessions are lost on restart and inconsistent across multiple workers.

Actions:

- Define a durable session storage strategy using the existing database or Redis layer.
- Persist owner identity, learner identity, mastery inputs, item sequence, current index, and response state.
- Add migration if database-backed.
- Add expiry and cleanup behavior.

Acceptance checks:

- Practice sessions survive API process restart in the chosen storage layer.
- Multi-worker access is consistent.
- Expired sessions cannot be advanced.

## Phase 3 - Frontend Build and Test Health

Priority: P0

### 3.1 Reconcile Frontend Dependencies

Problems addressed:

- `dexie` is declared and locked but not resolvable from installed `node_modules`.
- The checked-out frontend dependency state does not match the manifest.
- Package manager context differs between global pnpm and `packageManager`.

Actions:

- Use the declared package manager version from `app/frontend/package.json`.
- Reinstall frontend dependencies from `pnpm-lock.yaml`.
- Verify `dexie` resolves.
- Document the expected frontend install command.

Acceptance checks:

- `pnpm install --frozen-lockfile` completes in `app/frontend`.
- `node -e "require.resolve('dexie')"` succeeds from `app/frontend`.

### 3.2 Fix Frontend TypeScript Errors

Problems addressed:

- `pnpm exec tsc --noEmit --pretty false` fails with implicit `any` errors.
- Dexie type resolution currently fails.

Actions:

- Fix explicit parameter types in offline cache/storage modules.
- Confirm Dexie imports/types compile after dependency reconciliation.

Acceptance checks:

- `pnpm exec tsc --noEmit --pretty false` passes from `app/frontend`.

### 3.3 Fix Vitest TSX Parsing

Problems addressed:

- Vitest fails 15 suites with JSX/TSX parse failures.
- Current JSX/compiler settings do not match the active Vite/Vitest/Rolldown path.

Actions:

- Adjust Vitest/Vite TypeScript JSX handling.
- Keep Next.js build settings compatible.
- Avoid test-only hacks that diverge from application compilation.

Acceptance checks:

- `pnpm exec vitest run --reporter=dot` passes from `app/frontend`.
- A frontend CI job runs install, typecheck, and tests from `app/frontend`.

## Phase 4 - Runtime and Environment Alignment

Priority: P0

Problems addressed:

- `.python-version` says Python 3.12.3.
- Docker uses Python 3.11.
- Remote venv uses Python 3.11.0rc1.
- CI mostly uses Python 3.12.3.
- Requirements are generated with Python 3.12 metadata.

Actions:

- Choose the supported production Python version.
- Align `.python-version`, Dockerfiles, CI, local setup docs, and lock/requirements generation.
- Rebuild the VM venv with the chosen stable version.
- Remove Python release-candidate runtimes from production-like verification.

Acceptance checks:

- `python --version` in local/CI/Docker contexts matches the chosen version.
- Backend smoke tests pass on the chosen version.
- Requirements metadata matches the chosen version.

## Phase 5 - Migrations and Schema Management

Priority: P1

Problems addressed:

- App startup performs production schema repair.
- Migration commands fail without environment preparation.
- Runtime startup repair overlaps with Alembic responsibility.

Actions:

- Convert startup schema repair into explicit Alembic migrations or a controlled migration job.
- Remove production schema mutation from application startup after migration coverage exists.
- Make `alembic current` and `alembic upgrade head` usable in local and CI environments.
- Add migration verification to CI.

Acceptance checks:

- `alembic upgrade head` succeeds in an isolated test database.
- `alembic current --verbose` reports the expected head.
- API startup does not mutate production schema.

## Phase 6 - Durable Background Jobs

Priority: P1

Problems addressed:

- API routes return job IDs for FastAPI `BackgroundTasks`.
- Work is lost if the API process restarts.
- ARQ job code exists but is not deployed.
- ARQ settings references likely use wrong casing.

Actions:

- Fix ARQ settings references.
- Decide which workloads must use durable queueing.
- Wire ARQ worker into Compose and production deployment.
- Add health/readiness checks for worker/Redis connectivity.
- Stop presenting non-durable background tasks as durable jobs.

Acceptance checks:

- ARQ worker starts in local Compose.
- Durable job tests cover enqueue, execution, and status retrieval.
- API restart does not lose queued durable work.

## Phase 7 - Deployment and Security Hardening

Priority: P1

Problems addressed:

- Stripe success/cancel URLs are hardcoded to localhost.
- Nginx auth rate limit targets `/api/v1/auth/` while active routes are `/api/v2/auth/`.
- ACA Bicep uses wildcard CORS.
- Production secrets are passed directly as environment variables in Compose.
- `/metrics` and dev diagnostic routes need deployment-level decisions.

Actions:

- Move Stripe redirect URLs to environment-derived public frontend URLs.
- Fix Nginx auth rate-limit path.
- Replace wildcard CORS with explicit allowed origins.
- Define which deployment target is authoritative: Compose, ACA, or another path.
- Retire or mark non-authoritative deployment drafts.
- Put production secrets behind the target platform's secret-management mechanism.
- Decide whether `/metrics` is private-network only or requires app-level protection.
- Restrict `/__dev/slow_query` to explicitly allowed development contexts.

Acceptance checks:

- Production config contains no localhost redirect defaults.
- Nginx rate limits apply to active auth routes.
- ACA CORS does not use `*`.
- Secret handling is platform-native or explicitly documented as local-only.

## Phase 8 - Privacy and Authorization Completion

Priority: P1

Problems addressed:

- POPIA legal-hold and export-offered checks are TODOs.
- Auth extended export/deletion task enqueueing is TODO.
- Some authorization checks have repository-backed TODOs.

Actions:

- Implement legal-hold checks before erasure.
- Ensure export-offered and deletion-request flows are persisted and auditable.
- Replace placeholder authorization checks with repository-backed enforcement.
- Add tests for POPIA erasure, export, consent expiry, and audit immutability paths.

Acceptance checks:

- POPIA workflows enforce legal hold and export preconditions.
- Erasure/export requests create auditable state transitions.
- Authorization tests fail closed when repository checks deny access.

## Phase 9 - Coverage, CI, and Evidence Renewal

Priority: P1

Problems addressed:

- Stored coverage artifact reports 40.9 percent, below declared threshold.
- Mypy and quality checks are partially non-blocking.
- Documentation has stronger claims than current executable evidence.

Actions:

- Regenerate coverage from the current commit.
- Decide the release coverage threshold and enforce it.
- Make correctness, frontend typecheck, frontend tests, import-linter, migration checks, and launch-content validation visible in CI.
- Keep broader lint/style debt tracked separately when not immediately release-blocking.

Acceptance checks:

- Current coverage report is regenerated and committed only if policy allows artifacts.
- CI fails on agreed release-blocking checks.
- Release documentation references current evidence, not stale artifacts.

## Phase 10 - Workspace Hygiene and Auditability

Priority: P2

Problems addressed:

- Ignored local state is large and can mislead audits.
- `.venv`, `.next`, `node_modules`, coverage output, caches, and pyc files inflate scans.

Actions:

- Add a safe cleanup target or script that removes ignored build/cache artifacts only after confirmation.
- Add audit inventory commands that operate on tracked files by default.
- Keep dependency installs reproducible.

Acceptance checks:

- Clean-checkout audit counts are reproducible.
- Scanners can run on tracked files without timing out on build artifacts.

## Initial Implementation Order

1. Add audit and roadmap artifacts.
2. Fix compileall syntax failure.
3. Fix `F821` release-blocking Ruff failures.
4. Secure practice session continuation routes with tests.
5. Fix frontend dependency/type/test gates.
6. Align CI gates with the checks above.
7. Proceed through runtime, migrations, jobs, deployment, and privacy hardening.

