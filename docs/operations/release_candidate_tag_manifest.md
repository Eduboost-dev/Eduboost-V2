# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-06-01T15:08:07.115471+00:00`
- branch: `remediation/phase0-phase1`
- commit: `7a24a9a7f59c5fba6ec62b983203d8e268932af4`
- release_candidate: `beta-7a24a9a7`

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
git tag -a beta-7a24a9a7 -m "Beta release candidate beta-7a24a9a7"
git push origin beta-7a24a9a7
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
