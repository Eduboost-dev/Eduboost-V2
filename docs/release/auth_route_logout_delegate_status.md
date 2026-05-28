# Auth Route Logout/Revoke Delegation Status

Generated at: `2026-05-28T12:10:13Z`
Commit: `80170cbc24b1379aeaf351f1c4f387c65bc502ca`

**Status:** `auth-route-logout-delegation-passing`

| Route | Exists | Auth service param | Delegates | Direct route logic | Passed |
|---|---:|---:|---:|---|---:|
| `logout` | True | True | True | `-` | True |
| `revoke_all_tokens` | True | True | True | `-` | True |

## Blockers

- None

## No false-closure rules

- Route body delegation does not prove HTTP behavior.
- Logout/revoke HTTP proof remains a separate batch.
- This cleanup does not approve beta release.
