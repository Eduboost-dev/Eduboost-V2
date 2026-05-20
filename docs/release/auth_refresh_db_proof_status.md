# Auth Refresh DB Proof Status

Generated at: `2026-05-20T22:14:17Z`
Commit: `fe6b92247e119405439128bb45930e18779b3c32`

**Status:** `auth-refresh-db-proof-external-blocked`
**DSN present:** `False`
**Pytest return code:** `None`

## Evidence fields

| Field | Value | Valid | Reason |
|---|---|---:|---|
| `Database DSN label` | `pending` | False | pending |
| `Test command` | `pending` | False | pending |
| `Test result` | `pending` | False | pending |
| `Refresh persistence result` | `pending` | False | pending |
| `Logout revocation result` | `pending` | False | pending |
| `Revoke-all result` | `pending` | False | pending |
| `Reuse detection result` | `pending` | False | pending |
| `Evidence URL` | `pending` | False | pending |
| `Commit SHA` | `pending` | False | pending |
| `Verified by` | `pending` | False | pending |
| `Date verified` | `pending` | False | pending |

## Pytest summary

```text
AUTH_REFRESH_DB_PROOF_DSN not set; DB proof not executed
```

## Blockers

- AUTH_REFRESH_DB_PROOF_DSN is not set
- DB pytest did not pass
- evidence field Database DSN label: pending
- evidence field Test command: pending
- evidence field Test result: pending
- evidence field Refresh persistence result: pending
- evidence field Logout revocation result: pending
- evidence field Revoke-all result: pending
- evidence field Reuse detection result: pending
- evidence field Evidence URL: pending
- evidence field Commit SHA: pending
- evidence field Verified by: pending
- evidence field Date verified: pending

## No false-closure rules

- Skipped DB tests are not proof.
- Mock-only tests are not DB proof.
- AUTH_REFRESH_DB_PROOF_DSN must be explicit.
- Release mode requires accepted DB proof evidence.
