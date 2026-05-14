# Database Backup Manifest

Manifest ID: `0bee617ebd89ef3d`
Generated: `2026-05-14T21:15:25Z`
Branch: `codex/production_readiness`
Commit: `c9b255d6a61c7854da9ebea6d632b36b25d5995c`

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
