# Database Backup Manifest

Manifest ID: `aec26e2e30be661a`
Generated: `2026-05-24T20:42:29Z`
Branch: `code-archaeology`
Commit: `072c0678b1090169f2dbaac61ebaef4d636856d6`

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
