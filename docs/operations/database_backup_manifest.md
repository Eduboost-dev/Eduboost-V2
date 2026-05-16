# Database Backup Manifest

Manifest ID: `02852c8d84a92205`
Generated: `2026-05-16T19:14:29Z`
Branch: `codex/production_readiness`
Commit: `5b56bc7c5e95affe2f870cc85369d1ee43c49fc1`

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
