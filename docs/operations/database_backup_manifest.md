# Database Backup Manifest

Manifest ID: `0ccf74ece9bf55a2`
Generated: `2026-05-24T20:45:14Z`
Branch: `code-archaeology`
Commit: `f8e0b6cba09123135c9c4af0611f35c4bb2163ca`

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
