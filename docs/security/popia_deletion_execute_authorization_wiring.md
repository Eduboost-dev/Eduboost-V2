# POPIA Deletion Execute Authorization Wiring

## Endpoint

This slice enforces learner write authorization before job enqueue on:

```text
POST /api/v2/popia/deletion-execute/{learner_id}
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

The check runs before `enqueue_job(...)`, preventing unauthorized actors from
queuing physical purge work.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_deletion_execute_authorization_wiring.py \
  tests/integration/test_popia_deletion_execute_authorization.py \
  -q --no-cov
```
