# Phase 1 — T130 — Coverage Baseline

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Status:** Baseline established; full-suite coverage run is **blocked by test timeouts**.

---

## Executive summary

| Metric | Value | Notes |
|---|---|---|
| Tests collected | **2,698** | `pytest --collect-only` passes cleanly |
| Smoke tests | **32 passed** | Fast (~14s without coverage) |
| Unit test files | **522** | In `tests/unit/` |
| Integration test files | ~30 | In `tests/integration/` |
| CI coverage threshold | **60%** | Defined in `ci-cd.yml` |
| Full-suite coverage run | **Blocked** | Times out under coverage instrumentation |
| Subset coverage (78 tests) | **0.8%** | Not representative of full suite |

**Finding:** The test suite is large and well-structured, but running it under
coverage instrumentation causes timeouts. This means the **60% CI threshold
cannot currently be verified locally** and may not be met.

---

## Test inventory

### By test type

| Category | Count | Location | Approx runtime (no cov) |
|---|---|---|---|
| Smoke tests | 32 | `tests/smoke/` | ~14s |
| Unit tests | 522 files | `tests/unit/` | Unknown (estimated 5–10 min) |
| Integration tests | ~30 files | `tests/integration/` | Unknown (estimated 5–10 min) |
| POPIA tests | ~10 files | `tests/popia/` | Unknown |
| Content factory tests | ~15 files | `tests/unit/test_content_factory_*.py` | Unknown |

### Smoke test breakdown (verified passing)

```
tests/smoke/test_content_factory_admin_api_smoke.py
tests/smoke/test_content_factory_startup_flags.py
tests/smoke/test_v2_smoke.py  (main suite: 25 tests)
```

---

## Coverage run attempts

### Attempt 1: Full suite with coverage

```bash
pytest tests/unit tests/smoke --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** Process did not complete within reasonable time. Progress stopped
at ~31% of test execution. Likely cause: coverage instrumentation overhead on
async/SQLAlchemy-heavy tests causes individual tests to exceed implicit timeouts.

### Attempt 2: Unit tests only with coverage

```bash
pytest tests/unit --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** Timed out after 120 seconds. Progress reached ~16%.

### Attempt 3: Smoke tests only with coverage

```bash
pytest tests/smoke --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** Timed out after 60 seconds. Smoke tests pass in ~14s without
coverage but hang with coverage.

### Attempt 4: Small subset with coverage (successful)

```bash
pytest tests/unit/test_ai_safety_release_evidence.py \
       tests/unit/test_content_factory_enums.py \
       tests/unit/test_content_factory_route_security.py \
       tests/unit/test_warning_cleanup_contract.py \
       tests/smoke/test_v2_smoke.py \
       --cov=app --cov-report=term-missing
```

**Result:** 78 passed, 2 failed, 43.98s. Coverage: **0.8%** (subset only).

**Analysis:** The 0.8% is not representative. The subset tests are import and
contract tests that do not exercise application logic. A full suite run would
show significantly higher coverage, but the instrumentation issue prevents
measurement.

---

## Codebase size (measured from coverage XML)

| Package | Executable lines |
|---|---|
| `app.core` | 2,188 |
| `app.services` | 6,384 |
| `app.modules.*` | ~4,500 (aggregated) |
| `app.repositories` | 945 |
| `app.api_v2_routers` | ~1,200 |
| `app.api_v2_deps` | ~400 |
| `app.domain` | ~800 |
| `app.models` | ~500 |
| `app.security` | 201 |
| **Total** | **~22,237** |

See `audits/coverage/coverage_modules_20260527.txt` for the full per-package
breakdown.

---

## CI coverage gate status

`ci-cd.yml` defines:

```yaml
env:
  COVERAGE_THRESHOLD: "60"
```

And enforces it in the `unit-tests` and `v2-smoke` jobs:

```yaml
--cov-fail-under=${{ env.COVERAGE_THRESHOLD }}
```

**Risk:** If the full test suite does not achieve 60% coverage, the CI gate will
fail. The current timeout issue suggests this has not been validated recently.

---

## Root cause of coverage timeout

**Hypothesis 1:** Coverage instrumentation on async SQLAlchemy code causes
significant slowdown on test setup/teardown (DB session creation/rollback).

**Hypothesis 2:** Some tests make actual HTTP requests or LLM calls that are
slow; coverage makes them slower still.

**Hypothesis 3:** The `concurrency` setting in `.coveragerc` or `pytest.ini`
is not configured for async tests, causing serialization.

**Recommended investigation:**

```bash
# Run a single slow test with and without coverage to measure overhead
pytest tests/unit/test_slow.py -v --no-cov  # baseline
pytest tests/unit/test_slow.py -v --cov=app  # with coverage
```

---

## Next steps

| Task | Priority | Owner | Description |
|---|---|---|---|
| T130A | P1 | Engineering | Fix coverage timeout (investigate async/concurrency settings) |
| T131 | P1 | Engineering | Create coverage debt report (per-module target vs actual) |
| T132 | P2 | Engineering | Classify modules by coverage risk (P0/P1/P2) |
| T133 | P2 | Engineering | Identify "quick win" tests that add most coverage per effort |
| T134 | P2 | Engineering | Create coverage recovery sprint plan |
| T135 | P2 | Engineering | Add coverage to CI with realistic threshold |
| T136 | P2 | Engineering | Document coverage exemptions (e.g., generated code, boilerplate) |

---

## Validation commands

```bash
# Confirm collection is clean
.venv/bin/python -m pytest --collect-only --no-cov -q

# Confirm smoke tests pass (fast)
.venv/bin/python -m pytest tests/smoke --no-cov -q

# Attempt coverage (may timeout)
.venv/bin/python -m pytest tests/ --cov=app --cov-report=term-missing --no-cov-on-fail -q
```
