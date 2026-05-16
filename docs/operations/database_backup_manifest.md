# Database Backup Manifest

Manifest ID: `dac01a27b0db4a98`
Generated: `2026-05-16T17:32:40Z`
Branch: `codex/production_readiness`
Commit: `d4e487c8c7b550381dbc663675982b9d34784c36`

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
