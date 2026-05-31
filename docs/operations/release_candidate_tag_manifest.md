# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-28T13:53:01.932626+00:00`
- branch: `remediation/phase0-phase1`
- commit: `6f43341eb282b7f4983fc1c5954cda205f6ad1b9`
- release_candidate: `beta-6f43341e`

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
git tag -a beta-6f43341e -m "Beta release candidate beta-6f43341e"
git push origin beta-6f43341e
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
