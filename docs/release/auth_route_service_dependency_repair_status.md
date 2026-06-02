# Auth Route Service Dependency Repair Status

Generated at: `2026-05-22T14:17:20Z`
Commit: `ec48d99ff48d4ad08572fa300cd0d50b25fbc0ec`

**Status:** `auth-route-service-dependencies-passing`

| Function | Line | References auth_service | Has dependency param | Passed |
|---|---:|---:|---:|---:|
| `me` | 81 | False | False | True |
| `register` | 87 | True | True | True |
| `login` | 106 | True | True | True |
| `create_dev_session` | 124 | True | True | True |
| `refresh` | 148 | True | True | True |
| `list_sessions` | 179 | False | False | True |
| `logout` | 187 | True | True | True |
| `revoke_all_tokens` | 198 | True | True | True |

## Blockers

- None

## No false-closure rules

- F821-free route source does not prove HTTP auth behavior.
- Auth lifecycle HTTP proof remains separate.
- This repair does not approve beta release.
