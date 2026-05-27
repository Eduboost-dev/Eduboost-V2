# EduBoost V2 — Documentation Index

**Last updated:** 2026-05-27 (Phase 0 T070)

This directory contains the engineering, operations, governance, and product
documentation for EduBoost V2. Authoritative documents are listed below by
domain. The full corpus contains historical and reference material that is
not always current — when in doubt, prefer the documents linked below.

---

## ⚠️ Automated documentation freeze (Phase 0 → Phase 1)

**In effect from:** 2026-05-27 (Phase 0 T070 decision).
**Expected lift date:** End of Phase 1 (when production baseline gates pass —
see `EDUBOOST_V2_TODO_REVISED_27-May-2026.md` Phase 1 exit criteria).

### Why

The 2026-05-27 Technical State Audit observed that the `docs/` corpus had
grown to 1,018 Markdown files (~53 MB) and that the corpus was no longer
authoritative. Automated documentation generation was adding noise faster
than reviewers could validate it.

### Rules during the freeze

1. **No new auto-generated documentation may be committed.** Any script or
   CI workflow that writes Markdown into `docs/` must be paused or gated
   behind explicit human review.
2. **Human-authored Phase 0 / Phase 1 artifacts are exempt.** Evidence
   files under `audits/`, ADRs under `docs/adr/`, and operations contracts
   under `docs/operations/` are encouraged — they directly support audit
   remediation.
3. **PRs that touch `docs/` outside the exempt categories require a
   reviewer comment justifying the addition.** This is enforced socially
   for now; an automated gate may follow in Phase 1 J (T140 — CI workflow
   audit).
4. **Cleanup is welcome.** Deleting stale documentation during the freeze
   is in-scope and encouraged, provided the deletion is reviewed.

### Lifting the freeze

The freeze lifts when:

- The Phase 1 production-baseline gates (`coverage-gate`, `security-scans`,
  `migration-check`, `openapi-contract`, `observability-check`) are all
  consistently green on `master`.
- A successor ADR is committed defining the documentation governance model
  going forward (review cadence, deletion criteria, generation scope).

---

## Authoritative documents

### Architecture decisions (ADRs)

- `docs/adr/ADR-001-python-runtime-version.md` — supported Python runtime.

### Operations contracts

- `docs/operations/health.md` — health & readiness probe contract.
- `docs/operations/alertmanager.md` — Alertmanager deployment contract.

### Audits

- `audits/phase0/` — Phase 0 release blocker remediation evidence.

---

## Document discovery

The corpus is large. Prefer `git grep` over file-tree browsing:

```bash
git grep -l "<topic>" docs/
```

If you cannot find an authoritative document for a topic, that is itself
a finding — either the topic is genuinely uncovered (file a TODO task)
or the corpus has drifted and the link should be added to this index.
