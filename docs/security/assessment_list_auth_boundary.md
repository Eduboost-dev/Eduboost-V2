# Assessment List Authentication Boundary

## Endpoint

```text
GET /api/v2/assessments
```

## Boundary

This endpoint does not carry a `learner_id`, so it cannot use learner object
authorization. It now requires an authenticated user before exposing assessment
catalog data.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_assessment_list_auth_boundary.py -q --no-cov
```
