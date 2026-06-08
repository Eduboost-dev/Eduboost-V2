# Database Backup Manifest

Manifest ID: `93beccb242a03832`
Generated: `2026-06-08T12:36:05Z`
Branch: `fix/failing-tests`
Commit: `6b3c219669d08c2adae04015f40699bcbb153806`

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
