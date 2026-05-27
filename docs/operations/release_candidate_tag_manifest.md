# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-26T20:31:00.829080+00:00`
- branch: `pr-cf-013-full-generation-runner`
- commit: `3fd35da07070e6f6e8bc43ec0915d25ba53da6a7`
- release_candidate: `beta-3fd35da`

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
git tag -a beta-3fd35da -m "Beta release candidate beta-3fd35da"
git push origin beta-3fd35da
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
