# Data Retention Policy

Purpose: Define how long different classes of data are retained, the legal/operational basis, and disposal/erasure procedures.

Scope: Learner and guardian personal data, audit logs, diagnostics results, lesson content, analytics, backups, and infrastructure logs.

Retention categories and minimums
- Personal profile data (name, date of birth, contact details): retained while the account is active + 2 years after account deletion unless legal hold applies.
- Consent records: retained for 7 years from consent withdrawal or expiry for audit/compliance purposes.
- Diagnostic results and assessment scores: retained for 7 years by default (for longitudinal learning analytics and reporting), unless a data subject requests erasure.
- Lesson content and authoring artifacts: retained indefinitely for product improvement and reproducibility unless containing PII that a data subject requests removed.
- Audit logs (append-only audit repository): retained for 10 years and kept tamper-evident; specific audit events required by law may have longer retention.
- Backups (encrypted): retained for 90 days in staging/testing; production backup retention subject to ops policy and GDPR/POPIA requirements — document in `docs/secrets.md` and backup runbooks.
- Analytics/telemetry (aggregated): retained for 3 years in aggregated/hashed form. Raw event-level telemetry with identifiers should be purged or pseudonymized after 180 days.
- Authentication/session tokens (revocation logs): keep minimal traces needed for security investigations; purge detailed session contents after 90 days.

Data subject rights and erasure
- On verified erasure requests, remove or pseudonymize personal identifiers from operational datasets, while preserving necessary audit records that are legally required.
- Maintain an erasure log (admin-only) documenting requests, actions taken, and verification of completion.

Exceptions and legal holds
- Legal holds supersede retention schedules. Mark affected records as under hold and do not purge until hold is lifted.

Review cadence
- Review retention settings annually or when laws/regulations change.

Responsibilities
- Data owner: `NkgoloL` until a data governance owner is appointed.
- Engineering: implement retention enforcement (DB jobs, purge scripts, backup lifecycle).
- Compliance: validate retention, legal holds, and erasure workflows.

Implementation notes
- Prefer deletion by safe, auditable SQL jobs or background tasks that record deletion events in the audit ledger.
- For large-volume purges, use batched deletions and monitor for DB impact; prefer soft-delete plus background compaction where necessary.
