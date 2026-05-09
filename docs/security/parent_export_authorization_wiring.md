# Parent Access-Bundle Export Authorization Wiring

## Endpoint

This slice enforces per-learner read authorization inside:

```text
GET /api/v2/parents/{guardian_id}/export
```

The route already authorizes access to the guardian bundle. This slice adds a
per-learner check before including each learner export URL.

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_parent_export_authorization_wiring.py \
  tests/integration/test_parent_export_authorization.py \
  -q --no-cov
```
