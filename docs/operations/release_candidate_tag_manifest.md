# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-18T08:57:47.862341+00:00`
- branch: `fix/github-ci-cd-errors`
- commit: `7b41cde0e80010fe0537150ad5644202a9992e2a`
- release_candidate: `beta-7b41cde`

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
git tag -a beta-7b41cde -m "Beta release candidate beta-7b41cde"
git push origin beta-7b41cde
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
