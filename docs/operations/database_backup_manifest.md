# Database Backup Manifest

Manifest ID: `585702cd4f58e9dd`
Generated: `2026-05-17T20:41:00Z`
Branch: `codex/production_readiness`
Commit: `951aeca359fca7369b96643180bb01a640eccf3f`

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
