# Coverage Debt Register

**Owner:** Engineering
**Last updated:** 2026-05-27 (Phase 1 T131)
**Status:** Baseline established; recovery plan pending

---

## Current state

| Metric | Value | Target | Gap |
|---|---|---|---|
| Tests collected | 2,698 | — | — |
| Smoke tests passing | 32 | 32 | 0 |
| CI coverage threshold | — | 60% | Unknown |
| Actual coverage | **Unknown** | 60% | **Unknown** |
| Full-suite coverage run | Blocked by timeout | Required | **Blocked** |

**Critical finding:** We cannot currently measure coverage because running the
full test suite under coverage instrumentation times out. This must be fixed
before any coverage recovery work can be prioritized.

---

## Coverage timeout blocker (T130A)

### Symptoms

- `pytest tests/smoke --cov=app` times out after 60s (smoke tests pass in ~14s
  without coverage).
- `pytest tests/unit --cov=app` times out after 120s.
- Full suite coverage run does not complete.

### Likely causes

1. **Async SQLAlchemy instrumentation overhead:** Coverage on async ORM code
   causes significant slowdown in test setup/teardown (DB session creation and
   rollback).
2. **Missing concurrency config:** `.coveragerc` may not have
   `concurrency = greenlet` or `thread` set for async test compatibility.
3. **Synchronous coverage on async code:** The default coverage tracer is
   synchronous; async event loop switching adds overhead.

### Recommended fix

Add `.coveragerc` to the repository root:

```ini
[run]
branch = True
concurrency = greenlet,thread
dynamic_context = test_function
source = app

[report]
precision = 1
skip_covered = False
show_missing = True

[html]
directory = coverage_html
```

Then re-run:

```bash
.venv/bin/python -m pytest tests/smoke --cov=app --cov-report=term-missing -q
```

If this resolves the timeout, proceed to full-suite measurement.

---

## Module risk classification (T132)

Pending full coverage measurement. Preliminary classification based on module
complexity and criticality:

| Module | Lines | Criticality | Coverage risk | Rationale |
|---|---|---|---|---|
| `app.core.security` | ~200 | **P0** | High | JWT, auth, PII encryption — no tests = security blind spot |
| `app.core.token_config` | ~240 | **P0** | High | Token revocation, key rotation — must be tested |
| `app.core.config` | ~250 | **P0** | Medium | Settings validation — tested indirectly but needs direct tests |
| `app.api_v2_routers.auth` | ~200 | **P0** | High | Login/register/refresh — high user impact |
| `app.api_v2_routers.popia` | ~250 | **P0** | High | POPIA compliance — legal requirement |
| `app.services.jwt_keyring` | ~260 | **P0** | High | Key management — security-critical |
| `app.services.stripe_service` | ~200 | **P1** | High | Billing — financial impact |
| `app.services.content_factory` | ~1,500 | **P1** | High | Content generation — core product |
| `app.modules.consent` | ~300 | **P0** | High | POPIA consent — legal requirement |
| `app.modules.lessons` | ~1,800 | **P1** | Medium | Lesson generation — core product but complex |
| `app.repositories.*` | ~945 | **P1** | Medium | DB access — tested via integration but not directly |
| `app.modules.gamification` | ~400 | **P2** | Low | Gamification — nice-to-have |
| `app.modules.notifications` | ~250 | **P2** | Low | Notifications — lower user impact |
| `app.services.etl` | ~1,400 | **P2** | Low | ETL pipelines — admin-only, lower risk |

---

## Quick-win test opportunities (T133)

Pending coverage measurement. Likely high-impact, low-effort targets:

1. **JWT keyring tests** — `app/services/jwt_keyring.py` is pure Python with no
   external dependencies. A dedicated test file would add ~260 lines of coverage
   quickly.

2. **Token config tests** — `app/core/token_config.py` has clear input/output
   contracts (create/verify/revoke). ~240 lines of coverage.

3. **Security helper tests** — `app/core/security.py` has testable functions
   (hash_password, verify_password, encrypt_pii). ~200 lines.

4. **Auth router contract tests** — `app/api_v2_routers/auth.py` can be tested
   with FastAPI TestClient and mocked services. ~200 lines.

5. **POPIA router contract tests** — `app/api_v2_routers/popia.py` can be
   tested with mocked ConsentService. ~250 lines.

**Estimated quick-win impact:** ~1,150 lines of coverage (~5% of codebase) from
5 focused test files.

---

## Recovery sprint plan (T134)

### Sprint 1: Unblock measurement

- [ ] T130A: Add `.coveragerc` with async concurrency settings.
- [ ] Run full-suite coverage and record actual baseline.
- [ ] Document which tests are slow under coverage.

### Sprint 2: P0 security/auth coverage

- [ ] Add JWT keyring unit tests.
- [ ] Add token config unit tests.
- [ ] Add security helper unit tests.
- [ ] Add auth router contract tests.

### Sprint 3: P0 POPIA/consent coverage

- [ ] Add POPIA router contract tests.
- [ ] Add consent service unit tests.
- [ ] Add consent repository unit tests.

### Sprint 4: P1 core product coverage

- [ ] Add content factory service tests.
- [ ] Add lesson generation pipeline tests.
- [ ] Add assessment service tests.

### Sprint 5: P1 repository coverage

- [ ] Add direct repository tests with in-memory DB.
- [ ] Add integration tests for critical paths.

---

## Exemptions (T136)

The following code categories may be exempted from coverage targets with
justification:

| Category | Example | Exemption rationale |
|---|---|---|
| Auto-generated schemas | `app/domain/schemas.py` (Pydantic) | Boilerplate, tested implicitly via request validation |
| Alembic migrations | `alembic/versions/*.py` | One-way migration code, tested via `alembic upgrade head` |
| Dev-only fixtures | `app/api_v2_routers/auth.py` dev guardian | Guarded by `if not settings.is_production()` |
| Envelope route boilerplate | `app/core/envelope_route.py` | Framework wrapper, tested via integration |
| Health check endpoints | `app/api_v2.py` health/ready | Always public, always returns 200 — low value to unit test |

**Process:** Any new exemption requires PR approval from Engineering lead.

---

## Validation

```bash
# 1. Confirm collection is clean
.venv/bin/python -m pytest --collect-only --no-cov -q

# 2. Confirm smoke tests pass
.venv/bin/python -m pytest tests/smoke --no-cov -q

# 3. Attempt coverage (should not timeout after .coveragerc fix)
.venv/bin/python -m pytest tests/ --cov=app --cov-report=term-missing --no-cov-on-fail -q
```
