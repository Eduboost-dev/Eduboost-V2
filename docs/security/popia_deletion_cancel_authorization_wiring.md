# POPIA Deletion Cancel Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/popia/deletion-cancel/{learner_id}
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

Cancelling a pending deletion changes learner processing state and therefore
uses the write authorization policy.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_deletion_cancel_authorization_wiring.py \
  tests/integration/test_popia_deletion_cancel_authorization.py \
  -q --no-cov
```
