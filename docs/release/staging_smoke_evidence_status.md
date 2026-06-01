# Staging Smoke Evidence Status

Generated at: `2026-05-28T13:53:20Z`
Commit: `6f43341eb282b7f4983fc1c5954cda205f6ad1b9`
Branch: `remediation/phase0-phase1`

**Status:** `staging-smoke-evidence-not-accepted`
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``
**Run status:** ``
**Conclusion:** ``
**Head SHA:** ``
**Staging base URL:** ``
**Smoke command:** ``
**Smoke result:** ``
**Healthcheck result:** ``
**API result:** ``
**Frontend result:** `not-recorded`
**Verified by:** `unverified`
**Date verified:** `2026-05-28`

## Blockers

- no successful staging/smoke GitHub Actions run found for current commit; set STAGING_SMOKE_RUN_ID
- run ID is missing or non-numeric
- GitHub Actions run status is missing, expected completed
- GitHub Actions run conclusion is missing, expected success
- GitHub Actions run SHA missing does not match current commit 6f43341eb282b7f4983fc1c5954cda205f6ad1b9
- workflow name is missing
- staging base URL is missing, non-HTTPS, localhost/example, or placeholder
- staging smoke test command is missing or placeholder
- STAGING_SMOKE_RESULT must be passed
- STAGING_SMOKE_HEALTHCHECK_RESULT must be passed
- STAGING_SMOKE_API_RESULT must be passed

## No false-closure rules

- The accepted run must be completed and successful.
- The accepted run must match the current commit SHA.
- The staging URL must be a real non-placeholder HTTPS URL.
- The smoke command and result metadata must be explicit.
- The auth refresh DB proof workflow is not staging smoke evidence.
- This staging smoke evidence does not close legal/security/content approvals, JWT rotation, ARQ live Redis evidence, diagnostics live DB proof, lesson auth staging proof, or diagnostic scoring audit.
