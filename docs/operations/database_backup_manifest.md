# Database Backup Manifest

Manifest ID: `148bf35bb16746ac`
Generated: `2026-05-18T23:23:39Z`
Branch: `codex/production_readiness`
Commit: `4ff6f88a8962e9b06d305ac6d519b39e2e4b3e31`

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
