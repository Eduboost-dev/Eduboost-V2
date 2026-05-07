# Subprocessor Register

Purpose: Record third-party subprocessors used by EduBoost-V2, their purpose, data processed, and contact/security details.

NOTE: Fill production vendor details and contractual references.

1. Azure (or cloud provider)
- Purpose: Hosting, managed databases, object storage, key management
- Data processed: infrastructure metadata, optionally encrypted backups
- Data protection contact/contract: TODO — add subscription/account and data processing agreement reference

2. Email provider (e.g., SendGrid / Mailer)
- Purpose: Transactional email (verification, password reset, notifications)
- Data processed: email addresses, transactional content
- Contact/contract: TODO

3. Analytics provider (e.g., Segment, PostHog)
- Purpose: Product analytics and event collection
- Data processed: event metadata (pseudonymized IDs recommended)
- Contact/contract: TODO

4. LLM provider(s)
- Purpose: AI lesson generation and augmentation
- Data processed: non-PII prompts and structured context only; never send raw learner PII
- Contact/contract: TODO; ensure Data Processing Agreements and security reviews

5. Payment/billing provider (if used)
- Purpose: Payment processing and subscription lifecycle
- Data processed: payment metadata (tokens, customer IDs) — never store raw card PANs
- Contact/contract: TODO

6. Monitoring and error-reporting (e.g., Sentry, Datadog)
- Purpose: Observability, alerts, and error aggregation
- Data processed: stack traces (redact PII in logs before sending)
- Contact/contract: TODO

Maintaining the register
- Add vendor name, contact, DPA link, data categories processed, and last-reviewed date for each entry.
- Review the register annually or when adding/removing subprocessors.
