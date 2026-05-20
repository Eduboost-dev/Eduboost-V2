# Auth Route Logout/Revoke Delegation Status

Generated at: `2026-05-20T17:05:03Z`
Commit: `02ce769ddc0e49936eb829e87676ad4ed2fd2340`

**Status:** `auth-route-logout-delegation-not-proven`

| Route | Exists | Auth service param | Delegates | Direct route logic | Passed |
|---|---:|---:|---:|---|---:|
| `logout` | True | False | True | `-` | False |
| `revoke_all_tokens` | True | False | True | `-` | False |

## Blockers

- logout route is not fully delegated to auth service
- revoke_all_tokens route is not fully delegated to auth service

## No false-closure rules

- Route body delegation does not prove HTTP behavior.
- Logout/revoke HTTP proof remains separate.
- This cleanup does not approve beta release.
