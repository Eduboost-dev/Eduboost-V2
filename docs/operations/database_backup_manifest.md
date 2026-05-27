# Database Backup Manifest

Manifest ID: `fd1e6a8a9b9548cc`
Generated: `2026-05-26T20:29:19Z`
Branch: `pr-cf-013-full-generation-runner`
Commit: `3fd35da07070e6f6e8bc43ec0915d25ba53da6a7`

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
