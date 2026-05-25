# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-24T20:46:47.235687+00:00`
- branch: `code-archaeology`
- commit: `f8e0b6cba09123135c9c4af0611f35c4bb2163ca`
- release_candidate: `beta-f8e0b6c`

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
git tag -a beta-f8e0b6c -m "Beta release candidate beta-f8e0b6c"
git push origin beta-f8e0b6c
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
