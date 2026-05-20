# Auth Refresh DB Proof Evidence

**Item:** AUTH-REFRESH-DB-PROOF-001

**Database DSN label:** pending

**Test command:** pending

**Test result:** pending

**Refresh persistence result:** pending

**Logout revocation result:** pending

**Revoke-all result:** pending

**Reuse detection result:** pending

**Evidence URL:** pending

**Commit SHA:** pending

**Verified by:** pending

**Date verified:** pending

## Required proof

- Refresh token is persisted after login/refresh flow.
- Logout invalidates the active refresh token.
- Revoke-all invalidates all user refresh tokens.
- Reuse of an already-consumed refresh token is rejected.
- Tests execute against a disposable real DB target, not a mock-only harness.

## No false-closure rule

This file is not proof while any required field is pending or any result field is not `passed`.
