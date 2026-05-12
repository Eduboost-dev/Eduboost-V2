# EduBoost V2 Technical State Report

Date assessed: 2026-05-12  
Workspace assessed: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2`  
Local branch assessed: `master` at `4a79e8b`  
Remote comparison: local `master` was 4 commits behind `origin/master` at `dbf203d`

## Executive Summary

EduBoost V2 is a substantial production-readiness implementation, but the
assessed checkout is not release-green. The architecture is coherent, the V2
runtime imports, OpenAPI drift checks pass, route inventory checks pass, and the
frontend lint/type/test loop is healthy. However, the broad backend unit gate is
currently red with a mix of post-merge contract regressions, a missing
documentation artifact, and database-dependent tests that still fail when a
local PostgreSQL instance is unavailable.

The project should be described as:

- implemented in many critical areas,
- partially verified on targeted runtime/frontend checks,
- not currently clean on the aggregate backend/unit quality gate,
- not ready for a confident production or public-beta claim from this checkout.

## Repository State

### Branch And History

- Local checkout: `master`
- Local HEAD: `4a79e8b`
- Remote `origin/master`: `dbf203d`
- Divergence at assessment time: local branch was `0 ahead / 4 behind`

Recent integrated work in the local history includes:

- PRs #111 through #120 covering lazy DB fixture setup, Node 20 declaration,
  lint cache behavior, Cluster H Makefile wiring, local DB tolerance, frontend
  E2E workflow wiring, POPIA workflow repair, DB backup workflow branch
  retargeting, and frontend lockfile sync.
- Follow-on repository hardening and backlog restructuring commits.

### Repository Scale Snapshot

- Python files across `app`, `tests`, and `scripts`: `869`
- Frontend `.ts` / `.tsx` files outside `node_modules`: `69`
- GitHub workflow files: `25`
- Production-readiness backlog files: `21`
- Open backlog checkboxes: `1236`
- Completed backlog checkboxes: `30`

This is not a thin prototype. It is a large application plus a large evidence
and readiness apparatus, with the main risk now shifting from feature absence to
verification consistency and signal quality.

## Architecture Assessment

### Backend

The backend remains centered on a modular FastAPI runtime:

- Canonical runtime: `app.api_v2:app`
- Compatibility shim: `app.legacy.api.main:app`
- Core layers present:
  - routers under `app/api_v2_routers`
  - services under `app/services`
  - repositories under `app/repositories`
  - domain contracts under `app/domain`
  - bounded modules under `app/modules`

The runtime contract is coherent and still passes direct verification:

- `make runtime-check` passed
- `make openapi-check` passed
- `make route-inventory-check` passed
- Explicit import smoke checks passed for:
  - `app.api_v2`
  - `app.repositories.lesson_repository`
  - `app.repositories.diagnostic_repository`
  - `app.repositories.assessment_repository`

Observed runtime metadata from `make runtime-check`:

- `app.api_v2:app`: 143 routes
- `app.legacy.api.main:app`: 144 routes

### Frontend

The frontend is a Next.js application under `app/frontend` with:

- React 18
- Next 14
- Vitest
- TypeScript
- Node runtime requirement now declared as `>=20`

The local frontend quality loop is healthy in the assessed checkout:

- `npm run lint` passed
- `npm run type-check` passed
- `npm test -- --run` passed
  - 10 test files passed
  - 41 tests passed

Warnings remain:

- Vite CJS API deprecation warning
- React `act(...)` test warnings in routing tests

Those warnings are not immediate release blockers, but they are legitimate test
quality debt.

## Test And Quality State

### Broad Backend Unit Gate

Command run:

```bash
python3 -m pytest tests/unit -m "not llm and not e2e" --tb=short --no-cov -q
```

Observed result:

- `1283 passed`
- `18 failed`
- `16 errors`
- `11 skipped`
- Runtime: about 3 minutes

This is the most important current-state signal from the assessment: the unit
suite is broad, meaningful, and currently not green.

### Failure Classes

#### 1. Database-dependent item-bank tests still hard-fail without Postgres

Affected file:

- `tests/unit/modules/diagnostics/test_item_bank_pipeline.py`

Observed issue:

- 16 setup errors from `ConnectionRefusedError` on `127.0.0.1:5432`
- The file is marked as integration-like work, but it also carries its own
  module-scoped autouse DB setup that still forces a real local database.

Implication:

- The previous global fixture hardening was not enough to make the aggregate
  unit command locally resilient.
- The project still mixes integration-grade DB behavior into the `tests/unit`
  tree in a way that confuses expected execution semantics.

#### 2. Frontend E2E workflow evidence checks regressed after workflow cleanup

Affected contract/evidence tests include:

- `tests/unit/test_frontend_e2e_opt_in_workflow.py`
- multiple `tests/unit/test_cluster_g_*` files

Observed issue:

- The updated workflow uses direct npm/Playwright commands from
  `app/frontend`, but evidence checks still require the literal strings:
  - `make frontend-e2e-mocked`
  - `make frontend-e2e-smoke`

Implication:

- The workflow behavior may be valid, but the repo's own contract checkers were
  not updated in tandem.
- The project currently has a tooling/spec mismatch, not simply a missing
  feature.

#### 3. `PR_INTEGRATION_SUMMARY.md` is referenced but absent

Affected checks:

- `tests/unit/test_pr002r_docs_contract.py`
- `tests/unit/test_pr002r_evidence_check.py`

Observed issue:

- `PR_INTEGRATION_SUMMARY.md` is required by evidence scripts and referenced by
  documentation, but is missing from the checkout.

Implication:

- PR-002R evidence and release-state snapshot checks are internally
  inconsistent.
- The docs/evidence layer currently claims a file that does not exist.

### Makefile Hygiene Warnings

The successful Makefile-driven checks emit parse-time duplicate-target warnings:

- `observability-ops-check`
- `post-deploy-staging-smoke-checklist-check`
- `release-candidate-tag-manifest-check`
- `release-state-snapshot-check`
- `staging-smoke-evidence-manifest-check`

Each of these appears twice in `Makefile`, causing later recipes to override
earlier ones. This did not fail the commands I ran, but it is a real maintenance
hazard because the effective behavior depends on declaration order.

## CI And Workflow Posture

The repo contains a mature CI surface with workflows covering:

- runtime and OpenAPI contracts
- auth boundaries
- POPIA consent/audit evidence
- item-bank CI
- cluster-specific release evidence
- DB backup dry-run and matrix paths
- frontend E2E opt-in workflows
- release automation

This is a strong foundation. The current issue is not lack of CI intent; it is
workflow-contract drift after recent merges.

Specific CI observations:

- DB backup workflows now target `master`, which matches the repository's
  active production branch.
- POPIA workflow wiring has been repaired to include the closure test path.
- Frontend opt-in workflow is now aligned to `app/frontend`, but supporting
  evidence checks still expect old Makefile command text.

## Documentation And Backlog Posture

The repository now uses a split production-readiness backlog under:

- `TODO.md`
- `docs/backlog/production_readiness/*.md`

The split is helpful for parallel ownership, but the counts still show a large
remaining implementation/verification burden:

- 1236 open checklist items
- 30 completed checklist items

Important posture documents are present:

- `README.md`
- `docs/current_state.md`
- `docs/project_status.md`
- `docs/technical_state_report_2026-05-11.md`

The documentation quality is generally thoughtful and disciplined about claim
levels. However, there is a freshness problem:

- `docs/current_state.md` and the 2026-05-11 report describe a stronger verified
  posture than the 2026-05-12 unit-suite run currently supports.
- The docs should be treated as historical or conditional until the latest
  regressions are fixed and revalidated.

## Production Readiness Assessment

### Stronger Areas

- Canonical backend runtime and importability
- OpenAPI and route inventory generation
- Modular backend structure
- Frontend local lint/type/test health
- Rich CI/evidence framework
- Explicit current-state and claim-discipline documentation

### Weaker Areas

- Aggregate backend/unit gate not green
- Integration-style DB tests still leaking into a nominal unit path
- Evidence scripts and workflow implementation drifted apart
- Missing `PR_INTEGRATION_SUMMARY.md`
- Duplicate Makefile targets
- Local checkout behind remote branch at assessment time

## Recommended Priority Order

1. Restore a green backend/unit gate.
   - Resolve the item-bank DB fixture behavior in the aggregate test path.
   - Decide whether those tests remain under `tests/unit` or move to a strictly
     integration-class execution path.

2. Reconcile Cluster G/frontend workflow evidence checks with the updated E2E
   workflow implementation.
   - Either restore the expected `make` command usage or update the evidence
     scripts/docs/tests to the new npm/Playwright invocation contract.

3. Restore or retire `PR_INTEGRATION_SUMMARY.md`.
   - The repository currently references it as a required evidence artifact.

4. Remove duplicate Makefile target definitions.
   - This reduces invisible override behavior and future CI confusion.

5. Re-run the full local verification story on a checkout synced to
   `origin/master`.
   - The assessed worktree was 4 commits behind remote.

6. Refresh `docs/current_state.md` and the dated technical report once the
   regressions above are fixed.

## Bottom Line

EduBoost V2 is no longer in a "does the project exist?" phase. It is in a much
harder and more valuable phase: aligning implementation, CI contracts,
documentation, and release evidence so they all tell the same truth.

As of 2026-05-12, the project has a credible production-readiness architecture
and a healthy frontend local loop, but the assessed checkout is not yet
release-green because the backend aggregate quality gate and several
evidence-contract checks are still failing.
