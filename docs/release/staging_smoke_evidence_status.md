# Staging Smoke Evidence Status

Generated at: `2026-05-21T19:06:12Z`
Commit: `a195b5eea80d648d8b748ebf48885caf42f77a58`
Branch: `codex/production_readiness`

**Status:** `staging-smoke-evidence-accepted`
**Run ID:** `26247145077`
**Run URL:** `https://github.com/NkgoloL/Eduboost-V2/actions/runs/26247145077`
**Workflow:** `Staging Smoke`
**Run status:** `completed`
**Conclusion:** `success`
**Head SHA:** `a195b5eea80d648d8b748ebf48885caf42f77a58`
**Staging base URL:** `https://eduboost-api.onrender.com`
**Smoke command:** `python scripts/staging_smoke_probe.py --base-url https://eduboost-api.onrender.com --health-path /health --api-path /api/v2/system/health --frontend-path /`
**Smoke result:** `passed`
**Healthcheck result:** `passed`
**API result:** `passed`
**Frontend result:** `passed`
**Verified by:** `github-actions`
**Date verified:** `2026-05-21`

## Blockers

- None

## No false-closure rules

- The accepted run must be completed and successful.
- The accepted run must match the current commit SHA.
- The staging URL must be a real non-placeholder HTTPS URL.
- The smoke command and result metadata must be explicit.
- The auth refresh DB proof workflow is not staging smoke evidence.
- This staging smoke evidence does not close legal/security/content approvals, JWT rotation, ARQ live Redis evidence, diagnostics live DB proof, lesson auth staging proof, or diagnostic scoring audit.
