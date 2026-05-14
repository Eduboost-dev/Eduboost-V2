# Database Backup Manifest

Manifest ID: `f68923056e239353`
Generated: `2026-05-14T12:57:22Z`
Branch: `codex/production_readiness`
Commit: `3471e25a64b695be1c66f046cfd543f647ac5fe6`

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
