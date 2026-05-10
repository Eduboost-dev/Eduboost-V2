# Final PR Merge Readiness Contract

## Purpose

This contract defines the final evidence required before merging the staging or
beta release-readiness PR.

## Merge Preconditions

- generated artifact hygiene check passes
- branch sync and rebase checklist passes
- beta evidence consistency check passes
- release state snapshot check passes
- final release verification check passes
- Cluster H release readiness check passes
- Cluster H closure check passes
- PR body contains verification, release boundary, rollback, evidence index, and known follow-ups
- no unresolved merge conflicts remain
- no generated `coverage.xml` conflict remains
- remote branch accepts non-force push

## Required Merge Evidence

- `docs/operations/release_state_snapshot.md`
- `docs/operations/beta_evidence_consistency_guard.md`
- `docs/operations/final_release_verification_bundle.md`
- `docs/operations/beta_release_pr_body.md`
- `docs/operations/CLUSTER_H_CLOSURE.md`

## Merge Boundary

Merging the release-readiness PR confirms evidence readiness. It does not itself execute deployment, approval, tagging, or production launch.

## Command

```bash
make final-pr-merge-readiness-check
```
