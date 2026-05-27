# Release Sign-off Manifest (Template)

This manifest collects named sign-offs required for a controlled beta go/no-go.
Fill real names, dates, and decisions once reviews complete.

Release candidate: `REPLACE_WITH_TAG_OR_SHA`
Snapshot reference: `docs/release/release_state_snapshot.md`

## Sign-offs

- **Release owner**: (name) — (date) — (decision: approve / defer / reject)
- **Technical lead**: (name) — (date) — (decision)
- **POPIA / Privacy**: (name) — (date) — (decision)
- **Security**: (name) — (date) — (decision)
- **Product**: (name) — (date) — (decision)
- **Rollback owner**: (name) — (date) — (decision)
- **Post-deploy verification owner**: (name) — (date) — (decision)

## Linked evidence

- Release state snapshot: [docs/release/release_state_snapshot.md](docs/release/release_state_snapshot.md)
- Unit tests evidence: [docs/release/unit_test_evidence.md](docs/release/unit_test_evidence.md)
- CI evidence: [docs/release/ci_run_evidence_status.json](docs/release/ci_run_evidence_status.json)
- Migration runbook: [docs/release/migration_runbook.md](docs/release/migration_runbook.md)

## Notes

- Use this manifest to capture names and decisions only — do not copy full
  evidence into this file. Evidence should remain in the referenced files.
