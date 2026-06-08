# CI Evidence Status

Generated at: `2026-06-08T12:35:51Z`
Commit: `6b3c219669d08c2adae04015f40699bcbb153806`
Branch: `fix/failing-tests`

**Status:** `ci-evidence-not-accepted`
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``
**Run status:** ``
**Conclusion:** ``
**Head SHA:** ``
**Verified by:** `unverified`
**Date verified:** `2026-06-08`

## Blockers

- no successful non-auth-refresh GitHub Actions run found for current commit
- run ID is missing or non-numeric
- GitHub Actions run status is missing, expected completed
- GitHub Actions run conclusion is missing, expected success
- GitHub Actions run SHA missing does not match current commit 6b3c219669d08c2adae04015f40699bcbb153806
- workflow name is missing

## No false-closure rules

- The accepted run must be completed and successful.
- The accepted run must match the current commit SHA.
- Placeholder run URLs or placeholder SHAs are rejected.
- The auth refresh DB proof workflow is not accepted as general CI evidence.
- This CI evidence does not close staging, external approvals, JWT rotation, ARQ live Redis evidence, diagnostics live DB proof, lesson authorization staging proof, or diagnostic scoring audit.
