# Database Backup Manifest

Manifest ID: `c57347c6beecc256`
Generated: `2026-05-28T13:50:15Z`
Branch: `remediation/phase0-phase1`
Commit: `6f43341eb282b7f4983fc1c5954cda205f6ad1b9`

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
