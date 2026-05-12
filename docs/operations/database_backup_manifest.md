# Database Backup Manifest

Manifest ID: `e49094c01c19168a`
Generated: `2026-05-12T20:05:38Z`
Branch: `fix/technical-state-report-implementation`
Commit: `84cad7993ac942ee5a2d0c8fb011dc0aee1301eb`

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
