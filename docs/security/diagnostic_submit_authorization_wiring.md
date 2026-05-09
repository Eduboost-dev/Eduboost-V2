# Diagnostic Submit Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/diagnostics/submit
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, body.learner_id)
```

The diagnostic submit endpoint mutates learner state by completing a diagnostic
session, updating theta, and persisting knowledge gaps. It is therefore treated
as a write operation.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin submits diagnostic | 200 |
| Guardian with learner claim submits diagnostic | 200 |
| Learner submits own diagnostic | 200 |
| Unrelated guardian | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_diagnostic_submit_authorization_wiring.py \
  tests/integration/test_diagnostic_submit_authorization.py \
  -q --no-cov
```
