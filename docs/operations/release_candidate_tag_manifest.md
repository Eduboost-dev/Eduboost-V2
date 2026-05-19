# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-18T23:24:30.784066+00:00`
- branch: `codex/production_readiness`
- commit: `4ff6f88a8962e9b06d305ac6d519b39e2e4b3e31`
- release_candidate: `beta-4ff6f88`

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
git tag -a beta-4ff6f88 -m "Beta release candidate beta-4ff6f88"
git push origin beta-4ff6f88
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
