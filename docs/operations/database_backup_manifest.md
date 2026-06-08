# Database Backup Manifest

Manifest ID: `69692c50cc6e507a`
Generated: `2026-06-08T15:25:55Z`
Branch: `fix/failing-tests`
Commit: `d8f1d702b13a2337b17e02f73b7edbabe91cf06f`

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
