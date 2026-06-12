# Phase 8: Privacy and Authorization Completion

**Branch:** `phase-8/privacy-and-authorization-completion`  
**Base:** `origin/master`  
**Status:** Planning

## Objective

Close all remaining P0 and P1 gaps in the authentication/authorization (PR-003) and
POPIA/privacy/audit (PR-004) production-readiness domains.  The work splits into two
tracks that can proceed partly in parallel.

---

## Track A — Authorization Completion (PR-003 gaps)

### A.1  Auth abuse-path tests  [P1]

- [ ] Add test: account lockout after `_MAX_FAILED_ATTEMPTS` consecutive failures
- [ ] Add test: lockout resets after cooldown or admin unlock
- [ ] Add test: security alert event emitted on suspicious auth patterns
- **Evidence:** `tests/unit/test_auth_abuse_paths.py`  
- **Files:** `app/services/auth_service.py`

### A.2  JWT `kid` rotation tests  [P1]

- [ ] Add test: token signed with `CURRENT_KID` verifies under current key
- [ ] Add test: token signed with `PREVIOUS_KID` verifies during overlap window
- [ ] Add test: unknown `kid` in token header raises appropriate error
- [ ] Add test: after rotation, new tokens use the new `kid`
- **Evidence:** `tests/unit/test_token_rotation.py`  
- **Files:** `app/core/token_config.py`

### A.3  Emergency revoke-all tests  [P1]

- [ ] Add test: `emergency_revoke_all` invalidates all existing tokens
- [ ] Add test: tokens created after revoke-all are not pre-emptively invalidated
- [ ] Add test: revoke-all is idempotent
- **Evidence:** `tests/unit/test_emergency_revocation.py`  
- **Files:** `app/core/token_config.py`

### A.4  Cookie security tests  [P1]

- [ ] Add test: refresh cookie is `HttpOnly`
- [ ] Add test: refresh cookie is `Secure` in production context
- [ ] Add test: refresh cookie has correct `SameSite` value
- [ ] Add test: cookie `Path` is scoped to `/api/auth`
- [ ] Add test: no access token stored in JavaScript-accessible storage
- **Evidence:** `tests/unit/test_cookie_policy.py`  
- **Files:** `app/core/cookies.py`, frontend token-storage audit (see A.5)

### A.5  Frontend token-storage audit  [P0]

- [ ] Audit frontend code for insecure token access-token storage
- [ ] Ensure access tokens are never stored in `localStorage` or `sessionStorage`
  directly readable by JS
- [ ] Fix any violations (move to `httpOnly` cookie or in-memory only)
- **Evidence:** `docs/security/frontend_token_storage_audit.md`

### A.6  Route policy matrix  [P1]

- [ ] Generate a complete route-policy matrix that documents:
  - Every public route
  - Every authenticated route
  - Required role for each route
  - Required consent gate for each route
  - Object-level authorization helper for each learner-data route
- [ ] Add CI check that matrix stays in sync with router registration
- **Evidence:** `docs/security/route_policy_matrix.md`, CI job

### A.7  Missing authorization tests  [P0 / P1]

- [ ] Test: teacher can access only assigned learners/classes
- [ ] Test: support operator cannot view unnecessary PII
- [ ] Test: compliance auditor can view audit records without broad data
  mutation rights
- [ ] Item-level reconciliation: ensure every learner-data router calls the
  correct `can_*` policy helper
- [ ] Test each router's authorization wiring (consolidate existing wiring
  tests into a single self-auditing registry)
- **Evidence:** `tests/unit/test_teacher_authorization.py`,
  `tests/unit/test_support_pii_boundary.py`,
  `tests/unit/test_compliance_auditor_boundary.py`

### A.8  Policy-based authorization (beyond RBAC)  [P1]

- [ ] Refactor sensitive workflows (data export, erasure, billing changes)
  from role-based checks to attribute/policy-based `can_*` helpers
- [ ] Ensure all `can_*` helpers return bool and are unit-tested
- **Evidence:** `app/core/authorization.py` (updated)

### A.9  Rate-limit tests  [P1]

- [ ] Test: login endpoint rate-limited after `LOGIN_LIMIT` requests
- [ ] Test: signup rate-limited after `SIGNUP_LIMIT`
- [ ] Test: password-reset rate-limited after `PASSWORD_RESET_LIMIT`
- [ ] Test: LLM lesson generation rate-limited after `LLM_LESSON_LIMIT`
- [ ] Test: account-level throttling keyed correctly
- [ ] Test: IP-level throttling keyed correctly
- **Evidence:** `tests/unit/test_rate_limits.py`

---

## Track B — Privacy & POPIA Completion (PR-004 gaps)

### B.1  Consent lifecycle implementation  [P0]

**Consent state machine:**

```
pending ──→ granted ──→ expired
  │                      │
  └──→ denied            │
         │               │
         └──→ withdrawn ─┘
                 │
                 └──→ renewal_required
```

- [ ] Define consent states in `app/domain/consent.py` (or extend existing)
- [ ] Implement consent grant flow: validate guardian identity, learner
  identity, privacy-notice version → create `granted` record
- [ ] Implement consent denial flow: create `denied` record with reason
- [ ] Implement consent withdrawal flow: transition `granted` → `withdrawn`
- [ ] Implement consent renewal flow: create new `granted` record with
  updated `expires_at`
- [ ] Implement consent expiry handling: scheduled job transitions
  `granted` → `expired` after TTL
- [ ] Implement restricted mode: when consent is not `granted`, learner-data
  routes return 403 with `consent_required` detail
- [ ] Tie consent record to privacy-notice version (semver)
- [ ] Tie consent record to guardian identity (FK)
- [ ] Tie consent record to learner identity (FK)
- [ ] Audit every consent state change (event, actor, old_state, new_state,
  timestamp)
- **Evidence:** `app/modules/consent/service.py` (extended),
  `app/models/consent.py` (or extend existing),
  `tests/unit/test_consent_lifecycle.py`

### B.2  Consent-gate negative tests  [P0]

- [ ] Negative test: analytics processing without consent → 403
- [ ] Negative test: RLHF feedback without consent → 403
- [ ] Negative test: parent reports without consent → 403
- [ ] Negative test: data export without consent/authority → 403
- [ ] Negative test: erasure request without authority → 403
- **Evidence:** `tests/unit/test_analytics_consent_gate_wiring.py`,
  `tests/unit/test_rlhf_consent_gate_wiring.py`,
  existing consent-gate wiring tests updated

### B.3  Data subject rights — Export workflow  [P0]

- [ ] Implement `POST /api/v2/data-subject/export` → creates export request
- [ ] Implement `GET /api/v2/data-subject/export/{id}/status`
- [ ] Implement `GET /api/v2/data-subject/export/{id}/download`
- [ ] Machine-readable JSON export format (all learner data grouped by
  category)
- [ ] Machine-readable CSV export format (flat rows)
- [ ] Guardian-friendly PDF export summary  [P1]
- [ ] SLA tracking: record `requested_at`, enforce 21-day POPIA window
- [ ] Notify guardian when export is ready  [P1]
- **Evidence:** `app/api_v2_routers/data_subject.py`,
  `app/services/data_subject_service.py`,
  `tests/integration/test_data_export_lifecycle.py`

### B.4  Data subject rights — Erasure workflow  [P0]

- [ ] Implement `POST /api/v2/data-subject/erasure` → creates erasure request
- [ ] Implement `GET /api/v2/data-subject/erasure/{id}/status`
- [ ] Implement erasure approval/review queue (admin reviews before execution)
- [ ] Implement erasure execution with audit-retention exceptions:
  - Soft-delete learner profile
  - Anonymize diagnostic/lesson data (retain aggregate stats)
  - Keep audit records (append-only, retain per legal hold)
- [ ] SLA tracking: record `requested_at`, enforce 21-day POPIA window
- [ ] Notify guardian when erasure completes  [P1]
- [ ] Admin review queue for billing/school/legal-retention conflicts  [P1]
- **Evidence:** `app/api_v2_routers/data_subject.py` (extend),
  `app/services/erasure_service.py`,
  `tests/integration/test_erasure_lifecycle.py`

### B.5  Data subject rights — Correction & Restriction  [P0]

- [ ] Implement correction/update workflow:
  `PUT /api/v2/data-subject/correction`
- [ ] Implement processing restriction workflow:
  `POST /api/v2/data-subject/restriction`
- [ ] Implement restriction status endpoint:
  `GET /api/v2/data-subject/restriction/{id}/status`
- **Evidence:** `app/api_v2_routers/data_subject.py` (extend),
  `tests/integration/test_correction_workflow.py`,
  `tests/integration/test_restriction_workflow.py`

### B.6  Data minimization & inventory  [P0]

- [ ] Create/update `docs/data_inventory.md` with table per domain:

  | Field | Purpose | Lawful basis | Retention | Access roles | 3rd-party exposure |
  |---|---|---|---|---|---|

- [ ] Inventory: learner fields
- [ ] Inventory: guardian fields
- [ ] Inventory: diagnostic fields
- [ ] Inventory: lesson/AI fields
- [ ] Inventory: billing fields
- [ ] Remove non-essential learner data fields
- [ ] Hash or tokenize identifiers where raw values unnecessary
- [ ] Separate identifiable operational data from analytics data
- [ ] Prevent names, emails, phone numbers, and raw identifiers from LLM
  prompts (audit existing prompt templates)
- [ ] Create `docs/data_retention_policy.md`  [P1]
- [ ] Create `docs/subprocessor_register.md`  [P1]
- **Evidence:** `docs/data_inventory.md`,
  `docs/data_retention_policy.md`,
  `docs/subprocessor_register.md`

### B.7  Audit integrity  [P0]

- [ ] Confirm sensitive events write to append-only PostgreSQL audit
  repository (verify `audit_log` table has no UPDATE/DELETE triggers
  from application role)
- [ ] Prevent application update/delete operations on audit records
  (DB-level permissions or `BEFORE` trigger that rejects writes)
- [ ] Add `event_hash` column to audit records (SHA-256 of concatenated
  event fields)
- [ ] Add `previous_event_hash` column to audit records (chained hash)
- [ ] Add HMAC/signature over `event_hash` with server-side secret
- [ ] Add audit-chain verification script
  (`scripts/verify_audit_chain.py`)
- [ ] Implement missing audit events:
  - [ ] Login success / failure
  - [ ] Token refresh
  - [ ] Logout
  - [ ] Consent grant / renewal / withdrawal / expiry
  - [ ] Learner profile create / update / delete
  - [ ] Diagnostic start / answer submission / completion
  - [ ] Lesson generation / LLM provider call
  - [ ] Parent report generation
  - [ ] Data export request / download
  - [ ] Erasure request / execution
  - [ ] Admin access (privileged read of learner data)
  - [ ] Billing changes
- [ ] Add immutable retention rules (legal hold flag, purge-after-TTL
  only via admin script)
- **Evidence:** `app/core/audit.py` (extended),
  `app/models/audit.py` (schema changes),
  `scripts/verify_audit_chain.py`,
  `tests/unit/test_audit_integrity.py`

### B.8  Legal / privacy documentation  [P0]

- [ ] Draft Security Disclosure Policy (`SECURITY.md` already exists — verify
  it covers disclosure expectations)
- [ ] Complete DPIA-style privacy impact assessment
  (`docs/legal/privacy_impact_assessment.md`)  [P1]
- [ ] Conduct legal review placeholder notes (add review-status section to
  each doc)  [P1]
- **Evidence:** `SECURITY.md` (verified),
  `docs/legal/privacy_impact_assessment.md`

---

## Track C — CI / Evidence Gates

### C.1  Authorization boundary CI  [P1]

- [ ] Add or update `.github/workflows/auth-boundary.yml` to run new
  authorization tests
- [ ] Add route-policy-matrix staleness check to CI

### C.2  Privacy boundary CI  [P1]

- [ ] Update `.github/workflows/privacy-boundary.yml` to run consent-lifecycle
  and audit-integrity tests
- [ ] Add data-inventory staleness check

### C.3  Coverage gates  [P1]

- [ ] Verify 80%+ unit-test coverage on `app/core/authorization.py`
- [ ] Verify 80%+ unit-test coverage on `app/modules/consent/`
- [ ] Verify 80%+ unit-test coverage on `app/core/audit.py`

---

## Execution Order

1. **A.1–A.4, A.9** (auth tests) — isolated, low-risk, fast to write
2. **A.5** (frontend token audit) — quick audit + potential fix
3. **A.7** (missing authorization tests) — broadens existing test matrix
4. **A.6** (route policy matrix) — depends on understanding all routes
5. **A.8** (policy-based authorization) — deeper refactor, do after tests
6. **B.1** (consent lifecycle) — core privacy domain, high priority
7. **B.2** (consent gate tests) — depends on B.1
8. **B.3–B.5** (data subject rights APIs) — new endpoints, moderate scope
9. **B.7** (audit integrity) — foundational, do before B.3–B.5 if possible
10. **B.6** (data inventory) — documentation, iterative
11. **B.8** (legal docs) — documentation, iterative
12. **C.1–C.3** (CI gates) — after all code changes

---

## Definition of Done

- [ ] All P0 and P1 checkboxes in `docs/backlog/production_readiness/03_authentication_sessions_rbac_and_object-level_authorization.md`
  are marked `[x]`
- [ ] All P0 and P1 checkboxes in `docs/backlog/production_readiness/04_popia_consent_privacy_data-subject_rights_and_audit.md`
  are marked `[x]` (or `[verified]` with evidence path)
- [ ] New tests pass on CI:
  ```
  pytest tests/unit/test_auth_abuse_paths.py \
         tests/unit/test_token_rotation.py \
         tests/unit/test_emergency_revocation.py \
         tests/unit/test_cookie_policy.py \
         tests/unit/test_rate_limits.py \
         tests/unit/test_teacher_authorization.py \
         tests/unit/test_support_pii_boundary.py \
         tests/unit/test_compliance_auditor_boundary.py \
         tests/unit/test_consent_lifecycle.py \
         tests/unit/test_audit_integrity.py \
         tests/integration/test_data_export_lifecycle.py \
         tests/integration/test_erasure_lifecycle.py \
         tests/integration/test_correction_workflow.py \
         tests/integration/test_restriction_workflow.py \
         -v
  ```
- [ ] All existing auth and consent tests continue to pass
- [ ] `make lint` passes with no new violations
- [ ] `docs/data_inventory.md`, `docs/data_retention_policy.md`,
  `docs/subprocessor_register.md` are committed
- [ ] This plan is marked **complete** and the PR is merged
