# Database Backup Manifest

Manifest ID: `669ef606ea384294`
Generated: `2026-05-15T18:57:11Z`
Branch: `codex/production_readiness`
Commit: `0bac413d3f09cb144fd6b8674f770e725ddc282f`

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
