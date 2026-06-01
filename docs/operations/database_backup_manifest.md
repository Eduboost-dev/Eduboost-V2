# Database Backup Manifest

Manifest ID: `1f63b5661fbc3842`
Generated: `2026-06-01T14:37:52Z`
Branch: `remediation/phase0-phase1`
Commit: `150d81e059f119a41073a7bbe6523b6f11661dea`

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
