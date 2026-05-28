# Release State Snapshot

**Generated:** 2026-05-27T20:50:42Z
**Commit:** d23b1869

This snapshot collects the minimal repository-side evidence available at the
time of capture. It is intended to be a concise index a release owner can use
to verify which artifacts exist in-repo and where to open them.

Key evidence files (representative, not exhaustive):

- Unit test evidence: [docs/release/unit_test_evidence.md](docs/release/unit_test_evidence.md)
- Last full successful local unit run: [docs/release/unit_latest_green.txt](docs/release/unit_latest_green.txt)
- CI run status: [docs/release/ci_run_evidence_status.json](docs/release/ci_run_evidence_status.json)
- Migration runbook: [docs/release/migration_runbook.md](docs/release/migration_runbook.md)
- Migration evidence: [docs/release/migration_evidence.md](docs/release/migration_evidence.md)
- Backup/restore evidence: [docs/release/db_backup_restore_rollback_evidence_status.md](docs/release/db_backup_restore_rollback_evidence_status.md)
- Release go/no-go status: [docs/release/release_go_no_go_status.md](docs/release/release_go_no_go_status.md)

Summary counts (quick glance):

- Unit evidence file present: yes
- CI evidence file present: yes
- Migration/runbook evidence: yes
- Operator runbooks/backup evidence: yes

How to update this snapshot

1. Re-run local evidence commands (unit tests, migrations, smoke checks).
2. Update the evidence files above with new outputs or links.
3. Update this snapshot `Commit` field and regenerate the timestamp.
