# Transaction Route Wiring Inventory

Generated at: `2026-06-01T14:41:25Z`

**Status:** `production-route-transaction-wiring-not-proven`

| Domain | Route function | File | Line | Mutation candidate | Transaction marker | Status |
|---|---|---|---:|---:|---:|---|
| `auth` | `me` | `app/api_v2_routers/auth.py` | 81 | False | False | `read-or-nonmutation-route` |
| `auth` | `register` | `app/api_v2_routers/auth.py` | 87 | True | False | `route-transaction-wiring-not-proven` |
| `auth` | `login` | `app/api_v2_routers/auth.py` | 106 | False | False | `read-or-nonmutation-route` |
| `auth` | `create_dev_session` | `app/api_v2_routers/auth.py` | 124 | True | False | `route-transaction-wiring-not-proven` |
| `auth` | `refresh` | `app/api_v2_routers/auth.py` | 148 | False | False | `read-or-nonmutation-route` |
| `auth` | `list_sessions` | `app/api_v2_routers/auth.py` | 179 | False | False | `read-or-nonmutation-route` |
| `auth` | `logout` | `app/api_v2_routers/auth.py` | 187 | False | False | `read-or-nonmutation-route` |
| `auth` | `revoke_all_tokens` | `app/api_v2_routers/auth.py` | 198 | False | False | `read-or-nonmutation-route` |
| `popia` | `grant_consent` | `app/api_v2_routers/popia.py` | 102 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `deny_consent` | `app/api_v2_routers/popia.py` | 119 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `withdraw_consent` | `app/api_v2_routers/popia.py` | 137 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `renew_consent` | `app/api_v2_routers/popia.py` | 152 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `create_export_request` | `app/api_v2_routers/popia.py` | 172 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `create_erasure_request` | `app/api_v2_routers/popia.py` | 190 | False | False | `read-or-nonmutation-route` |
| `popia` | `cancel_erasure` | `app/api_v2_routers/popia.py` | 205 | False | False | `read-or-nonmutation-route` |
| `popia` | `create_correction_request` | `app/api_v2_routers/popia.py` | 222 | False | False | `read-or-nonmutation-route` |
| `popia` | `create_restriction_request` | `app/api_v2_routers/popia.py` | 237 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `get_diagnostic_items` | `app/api_v2_routers/diagnostics.py` | 45 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `submit_diagnostic` | `app/api_v2_routers/diagnostics.py` | 102 | True | False | `route-transaction-wiring-not-proven` |
| `diagnostics` | `get_item_bank_coverage` | `app/api_v2_routers/diagnostics.py` | 165 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `get_item_bank_item` | `app/api_v2_routers/diagnostics.py` | 177 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `review_item_bank_item` | `app/api_v2_routers/diagnostics.py` | 214 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `start_diagnostic_session` | `app/api_v2_routers/diagnostics.py` | 250 | True | False | `route-transaction-wiring-not-proven` |
| `diagnostics` | `recover_diagnostic_session` | `app/api_v2_routers/diagnostics.py` | 266 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `diagnostic_next_item` | `app/api_v2_routers/diagnostics.py` | 282 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `diagnostic_respond` | `app/api_v2_routers/diagnostics.py` | 315 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `generate_lesson` | `app/api_v2_routers/lessons.py` | 33 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `generate_lesson_stream` | `app/api_v2_routers/lessons.py` | 58 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `get_lesson` | `app/api_v2_routers/lessons.py` | 81 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `complete_lesson` | `app/api_v2_routers/lessons.py` | 102 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `sync_lessons` | `app/api_v2_routers/lessons.py` | 119 | True | False | `route-transaction-wiring-not-proven` |

## Remaining boundaries

- route handlers must be wired through transactional application services
- live database transaction rollback behavior must be proven
- staging route smoke must be attached
- isolated rollback proof services do not prove production route wiring

## Interpretation

This inventory deliberately separates isolated rollback proof from production route wiring proof.
