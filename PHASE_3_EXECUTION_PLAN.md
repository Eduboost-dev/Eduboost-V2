# Phase 3 Execution Plan — Frontend Build and Test Health

**Date**: 2026-06-09 (updated after review)  
**Branch**: `phase-3/frontend-build-and-test-health`  
**Reviewed:** `docs/release/phase_3_plan_review.md` (6 gaps addressed)  
**Scope**: 3 interconnected frontend health checks (dependencies, TypeScript, Vitest)  
**Acceptance Criteria**: All CI gates passing for frontend build, type-check, and test suite

---

## Overview

Phase 3 addresses critical frontend build, type-checking, and test infrastructure gaps:

1. **3.1**: Reconcile frontend dependencies (pnpm, dexie resolution)
2. **3.2**: Fix frontend TypeScript compilation errors
3. **3.3**: Fix Vitest TSX parsing failures

All three components must pass in CI before merging to master.---

## Pre-Execution Baseline (Capture Before Starting)

Before any fixes, capture the current state for before/after comparison evidence:

```bash
# Save current TypeScript errors
cd app/frontend && npx tsc --noEmit --pretty false 2>&1 | tee /tmp/phase3_tsc_before.txt

# Save current Vitest output
cd app/frontend && npx vitest run --reporter=verbose 2>&1 | tee /tmp/phase3_vitest_before.txt
```

**Current known baseline (2026-06-09):**
- TypeScript: 4 errors (2 x accent/undefined in LessonRoadmap.tsx, 2 x dexie/module in schema.ts)
- Vitest: 15 suites reportedly failing (to be confirmed)
- pnpm: 9.14.4 installed, matches packageManager (no action needed)
- vitest.config.ts: @vitejs/plugin-react, jsdom, path aliases already configured

## Phase 3.1 — Reconcile Frontend Dependencies

### Problem Statement

- `dexie` is declared in `app/frontend/package.json` but not resolvable from `node_modules`
- Dependency state does not match manifest (lock file mismatch)
- Package manager mismatch: global pnpm vs. declared version in `packageManager` field

### Acceptance Criteria

- ✅ `pnpm install --frozen-lockfile` completes successfully in `app/frontend`
- ✅ `node -e "require.resolve('dexie')"` succeeds from `app/frontend`
- ✅ Frontend install command documented in `SYSTEM_STARTUP_GUIDE.md`

### Implementation Tasks

- [x] Verify pnpm version matches `packageManager` in `app/frontend/package.json` (confirmed: 9.14.4 == 9.14.4)
- [ ] Backup current `node_modules` state: `mv node_modules node_modules.bak`
- [ ] Clean install with `pnpm install --frozen-lockfile`
- [ ] **Fallback:** If `--frozen-lockfile` fails, run `pnpm install` (without frozen) to regenerate lockfile, then diagnose the drift before committing
- [ ] Verify dexie resolution: `node -e "require.resolve('dexie')"`
- [ ] Compare lockfile diff if fallback was used; commit updated lockfile only if drift is intentional
- [ ] Update local setup documentation in `SYSTEM_STARTUP_GUIDE.md` if changed
- [ ] Add `pnpm install --frozen-lockfile` to CI frontend job

---

## Phase 3.2 — Fix Frontend TypeScript Errors

### Problem Statement

- `npx tsc --noEmit --pretty false` fails with 4 TypeScript errors (verified 2026-06-09):
  1. `LessonRoadmap.tsx:426` -- `accent` is possibly undefined
  2. `LessonRoadmap.tsx:458` -- `accent` is possibly undefined
  3. `lib/db/schema.ts:1` -- Cannot find module `dexie`
  4. `lib/db/schema.ts:28` -- Property `version` does not exist on type `EduBoostOfflineDB`
- Dexie type resolution currently fails (depends on Phase 3.1 fixing module resolution)
- Note: `npx tsc` is used as the command; `pnpm exec tsc` is equivalent if pnpm is available

### Acceptance Criteria

- ✅ `npx tsc --noEmit --pretty false` passes from `app/frontend` (0 errors)
- ✅ All explicit parameter types are correctly annotated
- ✅ Dexie types resolve correctly

### Implementation Tasks

- [ ] Run `npx tsc --noEmit` and collect error list (baseline: 4 errors captured above)
- [ ] Fix error 1-2: Add null guard or non-null assertion for `accent` in `LessonRoadmap.tsx` (lines 426, 458)
- [ ] Errors 3-4 should resolve automatically after Phase 3.1 (dexie module + types)
- [ ] Verify `tsconfig.json` JSX settings (`jsx: preserve` is correct for Next.js)
- [ ] Re-run `npx tsc --noEmit` -- expect 0 errors
- [ ] Add `npx tsc --noEmit` to CI frontend job

---

## Phase 3.3 — Fix Vitest TSX Parsing

### Problem Statement

- Vitest reportedly fails 15 suites with JSX/TSX parse failures (2026-06-02 audit)
- The vitest.config.ts already includes @vitejs/plugin-react, jsdom environment, and path aliases -- the root cause may be simpler than a JSX config mismatch
- Dexie module resolution failures (Phase 3.1) may cascade into test failures
- Tests are currently unusable in CI
- **Coverage thresholds** (80% branches/functions/lines/statements) are aspirational. Phase 3 only requires tests to RUN; coverage targets are a Phase 9 concern.

### Acceptance Criteria

- ✅ `pnpm exec vitest run --reporter=dot` passes from `app/frontend`
- ✅ All 15 test suites execute (0 skip, 0 fail, all pass)
- ✅ Vitest configuration is documented

### Implementation Tasks

- [ ] **Discovery first:** Run `npx vitest run --reporter=verbose 2>&1 | head -100` to capture actual failures
- [ ] Diagnose root cause: JSX config, module resolution (dexie), or test setup issues
- [ ] If dexie-related: should resolve after Phase 3.1
- [ ] If JSX-related: audit `vitest.config.ts` vs TypeScript JSX settings (`jsx: preserve`)
- [ ] Ensure configuration does not diverge from Next.js build (`next.config` uses SWC, not Babel)
- [ ] Fix failing tests (do NOT lower coverage thresholds if tests are genuinely broken; skip coverage check with `--no-coverage` if needed)
- [ ] **Coverage note:** 80% thresholds in vitest.config.ts are aspirational; Phase 3 gates on test execution, not coverage percentage (Phase 9 handles coverage)
- [ ] Run full test suite: `npx vitest run --reporter=dot` -- expect all suites to pass
- [ ] Add `npx vitest run` to CI frontend job

---

## Frontend CI Job

Once all three components pass, the frontend CI job should run:

```yaml
- name: Frontend Dependencies
  run: cd app/frontend && pnpm install --frozen-lockfile

- name: Frontend TypeScript
  run: cd app/frontend && npx tsc --noEmit --pretty false

- name: Frontend Tests
  run: cd app/frontend && npx vitest run --reporter=dot
```

---

## Evidence Output

On completion, produce `docs/release/phase_3_evidence.md` containing:
- Before/after TypeScript error output
- Before/after Vitest test output
- pnpm install verification
- CI job configuration
- Any lockfile changes and rationale

## Success Criteria

**Phase 3 is complete when:**
- ✅ All 3 sub-phases have acceptance criteria met
- ✅ Frontend CI job passes on `master`
- ✅ No TypeScript or test failures remain
- ✅ `docs/release/phase_3_evidence.md` committed with before/after evidence
- ✅ Documentation updated

---

## Next Phase

After Phase 3 completes:
- **Phase 4**: Runtime and Environment Alignment (Python version standardization)
  - Align `.python-version`, Docker, CI, and local venv to Python 3.12.x
  - Run smoke tests on standardized version

---

## References

- Roadmap: `RoadMap.md` (Phase 3)
- Frontend source: `app/frontend/`
- TypeScript config: `app/frontend/tsconfig.json`
- Vitest config: `app/frontend/vitest.config.ts`
- Package manifest: `app/frontend/package.json`
