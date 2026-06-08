# Diagnostic Deep Health Runtime Evidence Status

Generated at: `2026-06-08T15:23:34Z`
Commit: `d8f1d702b13a2337b17e02f73b7edbabe91cf06f`
Branch: `fix/failing-tests`

**Status:** `diag-deep-health-runtime-not-accepted`
**Deep health URL:** ``
**HTTP status:** `None`
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``
**Run status:** ``
**Conclusion:** ``
**Head SHA:** ``
**Test command:** ``
**Verified by:** `unverified`
**Date verified:** `2026-06-08`

## Required component results

| Component | Result |
|---|---|
| `db` | `` |
| `migration` | `` |
| `audit` | `` |
| `session` | `` |

## Inferred response signals

| Component | Signal |
|---|---|
| `-` | `none inferred` |

## HTTP body excerpt

```text

```

## Blockers

- deep health URL is missing, non-HTTPS, localhost/example, or placeholder
- DIAG_DEEP_HEALTH_TEST_COMMAND is missing or placeholder
- deep health HTTP probe was not attempted
- DIAG_DEEP_HEALTH_DB_RESULT must be passed
- DIAG_DEEP_HEALTH_MIGRATION_RESULT must be passed
- DIAG_DEEP_HEALTH_AUDIT_RESULT must be passed
- DIAG_DEEP_HEALTH_SESSION_RESULT must be passed
- DIAG_DEEP_HEALTH_RUN_ID is required for accepted evidence

## No false-closure rules

- Lightweight staging smoke is not accepted as deep-health proof.
- HTTP 503 remains a blocker and must not be classified as runtime-passing.
- Required component results must explicitly be `passed`.
- The GitHub Actions run must be successful and match the current commit.
- This proof does not close JWT, ARQ, legal/security/content approvals, lesson auth, diagnostic scoring, or beta release.
