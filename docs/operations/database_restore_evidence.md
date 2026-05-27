# Database Restore Evidence

Generated: `2026-05-26T20:29:19Z`
Branch: `pr-cf-013-full-generation-runner`
Commit: `3fd35da07070e6f6e8bc43ec0915d25ba53da6a7`

## Restore Metadata

| Field | Value |
| --- | --- |
| Backup artifact ID | `pending-backup-artifact` |
| Target environment | `staging` |
| Integrity status | `pending` |
| Learner count status | `pending` |
| Consent count status | `pending` |
| Audit count status | `pending` |

## Required Verification Commands

```bash
make database-restore-dry-run
make runtime-check
make route-inventory-check
make popia-consent-closure-check
make cluster-d-closure-check
```

## Release Use

Production promotion is blocked until restore evidence records learner,
consent, and audit integrity status.
