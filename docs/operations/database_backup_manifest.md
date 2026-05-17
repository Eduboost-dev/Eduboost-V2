# Database Backup Manifest

Manifest ID: `96b880c0a24f6ee8`
Generated: `2026-05-17T21:24:59Z`
Branch: `codex/production_readiness`
Commit: `12709d957d0a0f3c618b885a109ef704477dc53a`

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
