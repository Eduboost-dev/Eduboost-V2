# Database Backup Manifest

Manifest ID: `d91aa5893b0f62de`
Generated: `2026-05-17T21:44:02Z`
Branch: `codex/production_readiness`
Commit: `2c2bd7fae4167979241dd5aedac5643ec1f1e461`

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
