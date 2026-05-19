# POPIA Route Transaction Slice Report

Generated at: `2026-05-19T17:34:27Z`
Commit: `688de8837d4e7991aa0dedf0b249fca78739a98b`

- Route file: `app/api_v2_routers/popia.py`
- Local status: `route-popia-delegation-not-proven`
- Live DB status: `external-blocked`
- Selected route count: `5`

## Route findings

| Route function | Line | Delegate calls | Direct DB mutations | Status |
|---|---:|---|---|---|
| `grant_consent` | 102 | `-` | `-` | `not-proven` |
| `deny_consent` | 120 | `-` | `-` | `not-proven` |
| `withdraw_consent` | 138 | `-` | `-` | `not-proven` |
| `renew_consent` | 153 | `-` | `-` | `not-proven` |
| `create_export_request` | 173 | `-` | `-` | `not-proven` |

## Transaction service markers found

- `.begin()`
- `TransactionalPOPIA`
- `TransactionalPOPIAConsentLifecycleService`

## Blockers

- grant_consent: no POPIA service delegate call found
- deny_consent: no POPIA service delegate call found
- withdraw_consent: no POPIA service delegate call found
- renew_consent: no POPIA service delegate call found
- create_export_request: no POPIA service delegate call found
- live-db: Live DB evidence URL is pending
- live-db: Test result is pending
- live-db: Database is pending
- live-db: Commit SHA is pending
- live-db: Verified by is pending
- live-db: Date verified is pending
- live-db: Live DB evidence URL must be a URL
- live-db: Test result must be passed/pass/green/ok
- live-db: Commit SHA must look like a git SHA

## No false-closure rules

- POPIA route delegation does not prove live database rollback.
- Service markers do not prove the production route path by themselves.
- ROUTE-TX-POPIA-001 release mode requires live DB evidence.
- TX-ROUTE-001 remains open until all mutation route slices are wired and proven.

## Interpretation

This report proves only the local POPIA route delegation slice. It does not prove live database rollback.
