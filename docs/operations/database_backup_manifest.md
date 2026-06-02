# Database Backup Manifest

Manifest ID: `31009b3ea2a40b61`
Generated: `2026-06-01T15:05:30Z`
Branch: `remediation/phase0-phase1`
Commit: `7a24a9a7f59c5fba6ec62b983203d8e268932af4`

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
