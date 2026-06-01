# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-06-01T14:40:28.943971+00:00`
- branch: `remediation/phase0-phase1`
- commit: `150d81e059f119a41073a7bbe6523b6f11661dea`
- release_candidate: `beta-150d81e0`

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
git tag -a beta-150d81e0 -m "Beta release candidate beta-150d81e0"
git push origin beta-150d81e0
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
