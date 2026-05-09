# Learner Authorization Coverage CI

## Workflow

```text
.github/workflows/learner-authz-coverage.yml
```

## Guard

The workflow runs:

```bash
make learner-authz-check
```

on pull requests and pushes targeting `master` and `release/**`.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_learner_authz_ci_contract.py -q --no-cov
```
