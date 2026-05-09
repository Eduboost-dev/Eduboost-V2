# POPIA Deletion Status Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/popia/deletion-status/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

Deletion status exposes learner data-rights state and is treated as a read
operation.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_deletion_status_authorization_wiring.py \
  tests/integration/test_popia_deletion_status_authorization.py \
  -q --no-cov
```
