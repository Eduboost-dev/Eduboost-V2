# Phase 2 Authorization Closure Report Generator

## Script

```text
scripts/generate_phase2_authorization_closure_report.py
```

## Output

```text
docs/security/PHASE2_AUTHORIZATION_CLOSURE.md
```

## Direct Execution

The script bootstraps the repository root onto `sys.path` so this command works
from the repository root:

```bash
python3 scripts/generate_phase2_authorization_closure_report.py
```

## Verification

```bash
python3 scripts/generate_phase2_authorization_closure_report.py
pytest -c pytest.ini tests/unit/test_generate_phase2_authorization_closure_report.py -q --no-cov
```
