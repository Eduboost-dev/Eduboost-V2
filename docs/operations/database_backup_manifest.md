# Database Backup Manifest

Manifest ID: `65c799fc7fe47651`
Generated: `2026-06-12T17:36:36Z`
Branch: `phase-11/technical-debt-burn-down`
Commit: `b33e49720860a084e7a7c42ead1b620cb859e64f`

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
