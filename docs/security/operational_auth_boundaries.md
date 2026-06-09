# Operational Auth Boundaries

## Purpose

This evidence document aggregates the non-learner-object operational routes
that were reviewed after Phase 2 learner-object authorization closure.

## Boundaries

| Route | Boundary |
| --- | --- |
| `POST /api/v2/auth/dev-session` | non-production only, hidden with production `404` |
| `POST /api/v2/admin/consent/trigger-renewal-reminders` | admin auth via `Depends(require_admin)` |
| `GET /api/v2/ether/onboarding/questions` | authenticated user via `Depends(get_current_user)` |

## Verification

```bash
pytest -c pytest.ini tests/unit/test_operational_auth_boundaries.py -q --no-cov
make learner-authz-check
make phase2-authz-closure
```
