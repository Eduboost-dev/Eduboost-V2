# Phase 3 Execution Plan — Frontend Build and Test Health

**Date**: 2026-06-09  
**Branch**: `phase-3/frontend-build-and-test-health`  
**Scope**: 3 interconnected frontend health checks (dependencies, TypeScript, Vitest)  
**Acceptance Criteria**: All CI gates passing for frontend build, type-check, and test suite

---

## Overview

Phase 3 addresses critical frontend build, type-checking, and test infrastructure gaps:

1. **3.1**: Reconcile frontend dependencies (pnpm, dexie resolution)
2. **3.2**: Fix frontend TypeScript compilation errors
3. **3.3**: Fix Vitest TSX parsing failures

All three components must pass in CI before merging to master.

---

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

- [ ] Verify pnpm version matches `packageManager` in `app/frontend/package.json`
- [ ] Clean `node_modules` and reinstall with `pnpm install --frozen-lockfile`
- [ ] Verify dexie resolution: `node -e "require.resolve('dexie')"`
- [ ] Update local setup documentation if needed
- [ ] Add pnpm install to CI frontend job

---

## Phase 3.2 — Fix Frontend TypeScript Errors

### Problem Statement

- `pnpm exec tsc --noEmit --pretty false` fails with implicit `any` errors
- Dexie type resolution currently fails (depends on Phase 3.1)
- TypeScript JSX configuration may be incomplete

### Acceptance Criteria

- ✅ `pnpm exec tsc --noEmit --pretty false` passes from `app/frontend`
- ✅ All explicit parameter types are correctly annotated
- ✅ Dexie types resolve correctly

### Implementation Tasks

- [ ] Run TypeScript check and collect error list
- [ ] Fix implicit `any` annotations in frontend source
- [ ] Verify `tsconfig.json` JSX settings are correct
- [ ] Verify Dexie types resolve after Phase 3.1
- [ ] Add typecheck to CI frontend job

---

## Phase 3.3 — Fix Vitest TSX Parsing

### Problem Statement

- Vitest fails 15 suites with JSX/TSX parse failures
- JSX/compiler settings do not match Vite/Vitest/Rolldown pipeline
- Tests are currently unusable in CI

### Acceptance Criteria

- ✅ `pnpm exec vitest run --reporter=dot` passes from `app/frontend`
- ✅ All 15 test suites execute (0 skip, 0 fail, all pass)
- ✅ Vitest configuration is documented

### Implementation Tasks

- [ ] Identify failing Vitest test suites
- [ ] Audit `vitest.config.ts` JSX/TS settings
- [ ] Compare with Vite and TypeScript configuration
- [ ] Fix JSX transform or preset mismatch
- [ ] Ensure configuration does not diverge from Next.js build
- [ ] Run full test suite and verify all suites pass
- [ ] Add Vitest to CI frontend job

---

## Frontend CI Job

Once all three components pass, the frontend CI job should run:

```yaml
- name: Frontend Dependencies
  run: cd app/frontend && pnpm install --frozen-lockfile

- name: Frontend TypeScript
  run: cd app/frontend && pnpm exec tsc --noEmit --pretty false

- name: Frontend Tests
  run: cd app/frontend && pnpm exec vitest run --reporter=dot
```

---

## Success Criteria

**Phase 3 is complete when:**
- ✅ All 3 sub-phases have acceptance criteria met
- ✅ Frontend CI job passes on `master`
- ✅ No TypeScript or test failures remain
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
