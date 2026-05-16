# Database Backup Manifest

Manifest ID: `5f19f4ce49f96b9b`
Generated: `2026-05-16T20:59:35Z`
Branch: `codex/production_readiness`
Commit: `eac64bb22a5e379e6a77e6053ce754a39c8147a0`

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
