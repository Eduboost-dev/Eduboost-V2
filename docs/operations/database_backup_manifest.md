# Database Backup Manifest

Manifest ID: `a8c55847d36481ea`
Generated: `2026-05-18T08:56:54Z`
Branch: `fix/github-ci-cd-errors`
Commit: `7b41cde0e80010fe0537150ad5644202a9992e2a`

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
