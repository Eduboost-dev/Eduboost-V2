# Staging Smoke Evidence

**Status:** pending runtime execution

This file must be updated after a real staging deployment smoke run.

## Required environment

| Field | Value |
|---|---|
| Staging URL | TODO |
| Commit SHA | TODO |
| Deployment ID | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required smoke checks

| Check | Expected result | Evidence |
|---|---|---|
| `GET /api/v2/health/deep` | `200 OK` with all critical checks healthy | TODO |
| `GET /api/v2/openapi.json` or published OpenAPI artefact | schema available and current | TODO |
| Auth register/login/refresh/logout | success path works; cookies/headers correct | TODO |
| Learner dashboard/read route | object authorization works | TODO |
| Lesson generation route | accepted or expected controlled response | TODO |
| Study plan generation route | accepted or expected controlled response | TODO |
| POPIA data export route | authorized path works; unauthorized path rejected | TODO |
| Security headers | expected headers present | TODO |
| CORS | allowed origin accepted; disallowed origin rejected | TODO |
| Observability | request appears in logs/traces/metrics | TODO |

## Command log

```bash
# paste commands and output here
```

## Decision

- [ ] Staging smoke passed.
- [ ] Staging smoke failed and release is blocked.
- [ ] Staging smoke partially passed; exceptions documented.
