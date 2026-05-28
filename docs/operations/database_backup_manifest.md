# Database Backup Manifest

Manifest ID: `830cc3f93892d66f`
Generated: `2026-05-28T12:36:13Z`
Branch: `remediation/phase0-phase1`
Commit: `80170cbc24b1379aeaf351f1c4f387c65bc502ca`

## Backup Metadata

| Field | Value |
| --- | --- |
| Backup artifact ID | `pending-backup-artifact` |
| Target environment | `staging` |
| Retention days | `30` |
| Encrypted | `yes` |

## Required Verification

- backup artifact is encrypted
- backup artifact ID is recorded
- retention period is recorded
- restore drill evidence is linked before production promotion

## Related Commands

```bash
make database-backup-dry-run
make database-backup-contract-check
make database-restore-drill-docs-check
```
