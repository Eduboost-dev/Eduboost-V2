# Database Backup Manifest

Manifest ID: `32448ce542799bee`
Generated: `2026-05-18T07:02:04Z`
Branch: `codex/production_readiness`
Commit: `d808cab9e62f4d3e23d9ea2691677c10e407cda7`

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
