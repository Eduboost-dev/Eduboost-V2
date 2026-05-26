# Database Backup Manifest

Manifest ID: `06894d5fedb7ad17`
Generated: `2026-05-26T16:06:04Z`
Branch: `pr-cf-013-full-generation-runner`
Commit: `f932279e2bf3d3524425915a4eb844816b078872`

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
