# CI Evidence Status

Generated at: `2026-05-26T16:03:25Z`
Commit: `f932279e2bf3d3524425915a4eb844816b078872`
Branch: `pr-cf-013-full-generation-runner`

**Status:** `ci-evidence-not-accepted`
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``
**Run status:** ``
**Conclusion:** ``
**Head SHA:** ``
**Verified by:** `unverified`
**Date verified:** `2026-05-26`

## Blockers

- no successful non-auth-refresh GitHub Actions run found for current commit
- run ID is missing or non-numeric
- GitHub Actions run status is missing, expected completed
- GitHub Actions run conclusion is missing, expected success
- GitHub Actions run SHA missing does not match current commit f932279e2bf3d3524425915a4eb844816b078872
- workflow name is missing

## No false-closure rules

- The accepted run must be completed and successful.
- The accepted run must match the current commit SHA.
- Placeholder run URLs or placeholder SHAs are rejected.
- The auth refresh DB proof workflow is not accepted as general CI evidence.
- This CI evidence does not close staging, external approvals, JWT rotation, ARQ live Redis evidence, diagnostics live DB proof, lesson authorization staging proof, or diagnostic scoring audit.
