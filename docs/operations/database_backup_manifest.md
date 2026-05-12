# Database Backup Manifest

Manifest ID: `5831bfc038eb63e0`
Generated: `2026-05-12T15:53:39Z`
Branch: `master`
Commit: `3502b2b51d4ea197249ea3baf5661e4ab9656c2f`

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
