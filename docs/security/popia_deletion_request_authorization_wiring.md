# POPIA Deletion Request Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/popia/deletion-request/{learner_id}
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

A deletion request changes learner processing state and is treated as a
write-sensitive learner-data rights operation.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_deletion_request_authorization_wiring.py \
  tests/integration/test_popia_deletion_request_authorization.py \
  -q --no-cov
```
