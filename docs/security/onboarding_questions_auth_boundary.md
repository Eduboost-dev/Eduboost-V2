# Onboarding Questions Authentication Boundary

## Endpoint

```text
GET /api/v2/onboarding/questions
```

## Boundary

This endpoint returns onboarding question catalog data. It does not carry a
`learner_id`, so it is guarded by authentication rather than learner object
authorization.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_onboarding_questions_auth_boundary.py -q --no-cov
```
