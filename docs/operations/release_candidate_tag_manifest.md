# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-19T19:43:31.560160+00:00`
- branch: `codex/production_readiness`
- commit: `e6b24b9d4c950c4d04681de5327a75cda597af02`
- release_candidate: `beta-e6b24b9`

## Tagging Convention

- beta release candidate tag format: `beta-<short-sha>` or explicit `RELEASE_CANDIDATE`
- release tags must point to reviewed commits
- release tags must be paired with beta release evidence bundle
- release tags must be paired with beta sign-off manifest
- release tags must be paired with rollback owner assignment

## Required Evidence Before Tagging

- `docs/operations/beta_release_evidence_bundle.md`
- `docs/operations/beta_signoff_manifest.md`
- `docs/operations/staging_smoke_evidence_manifest.md`
- `docs/operations/beta_rollback_runbook.md`
- `docs/operations/post_deploy_staging_smoke_checklist.md`

## Example Commands

```bash
git tag -a beta-e6b24b9 -m "Beta release candidate beta-e6b24b9"
git push origin beta-e6b24b9
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
