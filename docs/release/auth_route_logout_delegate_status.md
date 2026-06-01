# Auth Route Logout/Revoke Delegation Status

Generated at: `2026-06-01T14:29:08Z`
Commit: `150d81e059f119a41073a7bbe6523b6f11661dea`

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
