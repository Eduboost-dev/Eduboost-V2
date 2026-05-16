# Staging Smoke Evidence

**Status:** runtime smoke failed
<!-- Status: runtime smoke failed -->

- Captured at: `2026-05-16T07:15:14Z`
- Base URL: `https://staging.example.com`
- JSON evidence: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/staging_smoke_latest.json`

| Check | Method | Path | Expected | Actual | Passed | Error |
|---|---|---|---|---:|---|---|
| health_deep | GET | `/api/v2/health/deep` | `200,503` |  | no | URLError: <urlopen error [Errno -5] No address associated with hostname> |
| openapi | GET | `/openapi.json` | `200` |  | no | URLError: <urlopen error [Errno -5] No address associated with hostname> |
| security_headers | GET | `/api/v2/health` | `200,404` |  | no | URLError: <urlopen error [Errno -5] No address associated with hostname> |
| auth_register_shape | POST | `/api/v2/auth/register` | `201,400,409,422` |  | no | URLError: <urlopen error [Errno -5] No address associated with hostname> |
| popia_export_requires_auth | GET | `/api/v2/popia/data-export/smoke-learner` | `401,403,404` |  | no | URLError: <urlopen error [Errno -5] No address associated with hostname> |

## Decision

- [ ] Staging smoke accepted by release owner.
- [ ] Staging smoke rejected and release blocked.
