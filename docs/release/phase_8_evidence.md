# Phase 8 Evidence - Privacy and Authorization Completion

**Evidence date:** 2026-06-13  
**Status:** Partial; runtime POPIA data-rights issue found

## Evidence Sources

- `docs/roadmap/execution/phase_8_execution_plan.md`
- `docs/roadmap/execution/phase_8_implementation_report.md`
- `app/api_v2_routers/popia.py`
- `app/services/popia_service.py`
- `app/api_v2_deps/auth.py`
- Phase 8-related tests and security docs

## Current Passing Evidence

```text
.venv/bin/python scripts/check_privacy_boundary_evidence.py
# passed

.venv/bin/python -m pytest -q tests/unit/test_sprint3_popia_router_data_rights.py --no-cov
# 1 passed
```

## Current Failing or Contradictory Evidence

The current router injects `current_user` through `require_auth_context`, which returns `AuthContext`. `app/services/popia_service.py` expects dict-style `.get(...)` access in data export, erasure, correction, restriction, and execute-erasure flows.

Direct runtime proof from the 2026-06-13 audit:

```text
AttributeError: 'AuthContext' object has no attribute 'get'
```

`scripts/check_phase2_authorization_evidence.py` also fails because `app/api_v2_routers/ether.py` is missing.

## Evidence Gap

No `docs/release/phase_8_evidence.md` existed before this traceability repair. This file captures current evidence and does not support a full completion claim.

## Verdict

Phase 8 has useful tests and privacy documentation, but POPIA data-rights runtime paths are not fully proven and at least one path currently fails before database access.
