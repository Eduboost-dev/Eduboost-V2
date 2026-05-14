# EduBoost V2 — North Star TODO

**Purpose:** This file replaces the stale/root backlog-style TODO with an execution-focused North Star. It reflects work already completed in this conversation and the next work required before staging, beta, or production claims.

**Status vocabulary**

- `[x]` done: completed and locally/repository-side verified or explicitly confirmed done.
- `[verify]` implemented but needs fresh evidence, CI proof, staging proof, or artefact capture.
- `[ ]` open: not done.
- `[external]` requires a person/system outside normal code work.
- `[post-beta]` cannot be completed until beta has actually run.

---

## 0. Current project state

### Completed repository-side baseline

- [x] Production-readiness backlog domains 05–20 have repository-side implementation evidence, docs, check scripts, unit tests, and Makefile targets.
- [x] Domains 00–04 are treated as previously integrated into the repository-side baseline, with remaining legal/manual/runtime items separated below.
- [x] POPIA/consent/audit/source-evidence repair pass completed enough for the full unit suite to progress past prior POPIA failures.
- [x] Full backend unit suite reached near-green state: `1446 passed / 13 skipped / 1 failed`, with the remaining failure isolated to Alembic migration graph metadata.
- [x] Cluster H phantom-entry problem has been identified and converted into concrete remediation tasks.
- [x] Documentation claim discipline has been established: repository evidence must not be represented as legal, runtime, deployment, or launch approval.

### Current non-negotiable caveat

- [ ] EduBoost is **not public-beta-ready** with real learner data.
- [ ] EduBoost is **not production-launch-ready**.
- [ ] Next meaningful milestone is **full local green -> CI green -> staging execution evidence**.

---

## 1. Close the local green baseline

**Goal:** Make the local backend baseline fully green before any CI/staging claims.

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-01 | Apply Alembic migration graph repair. | `pytest -c pytest.ini tests/unit/test_migration_graph.py -q --no-cov` passes. | [verify] |
| NS-02 | Rerun full unit suite. | `pytest -c pytest.ini tests/unit -q --no-cov` output captured; expected result: all pass except intentional skips. | [ ] |
| NS-03 | Commit migration graph repair. | Git commit containing normalized migration file and removal of stale migration. | [ ] |
| NS-04 | Record local test evidence. | `docs/release/unit_test_evidence.md` or equivalent contains full output. | [ ] |

---

## 2. Make CI authoritative

**Goal:** Move from local-only verification to GitHub-verifiable evidence.

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-05 | Trigger GitHub Actions on this fork/repo. | Passing Actions run URL committed to `docs/release/ci_evidence.md`. | [ ] |
| NS-06 | Ensure OpenAPI drift check runs in CI. | CI job or Make target output proving `make openapi-check` passes. | [verify] |
| NS-07 | Ensure migration graph check runs in CI. | CI job output proving migration graph is linear and resolvable. | [ ] |
| NS-08 | Ensure POPIA gate/sweep runs in CI. | CI job output proving POPIA checks pass. | [ ] |
| NS-09 | Ensure frontend lint/type/unit checks run in CI. | CI output for lint, type-check, and tests. | [ ] |
| NS-10 | Add/verify branch protection on `master`. | Screenshot or settings export committed to `docs/release/branch_protection_evidence.md`. | [external] |

---

## 3. Repair release-governance evidence and Cluster H inflation

**Goal:** Replace symbolic Cluster H evidence with concrete release artefacts.

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-11 | H-01 | Run `make refresh-current-state` on a clean checkout. | Committed `docs/current_state.md` with timestamp and current gate results. | [ ] |
| NS-12 | H-02 | Create sign-off manifest with blank named fields. | `docs/release/sign_off_manifest.md`. | [ ] |
| NS-13 | H-03 | Create rollback runbook. | `docs/release/rollback_runbook.md` with literal API/frontend/database rollback commands and Alembic downgrade target. | [ ] |
| NS-14 | H-04 | Create post-deploy smoke checklist. | `docs/release/post_deploy_smoke_checklist.md` covering `/health/deep`, login, lesson generation, consent grant, POPIA export. | [ ] |
| NS-15 | H-05 | Create release bundle index. | `docs/release/release_bundle_v1.0.0-rc2.md` with real links only. | [ ] |
| NS-16 | H-06 | Add PR template. | `.github/PULL_REQUEST_TEMPLATE.md` with tests/docs/POPIA/security/migrations/rollback checkboxes. | [ ] |
| NS-17 | H-07 | Create release hygiene checklist. | `docs/release/release_hygiene_checklist.md`. | [ ] |
| NS-18 | H-14 | Create release state snapshot. | `docs/release/release_state_snapshot.md` with SHA, test counts, TODO counts, known issues, deferred items. | [ ] |
| NS-19 | H-17 | Create audit trail index. | `docs/release/audit_trail_index.md` mapping each claim to a readable artefact. | [ ] |
| NS-20 | H-26 | Replace 15 terminal Cluster H phantom entries with final closure certificate. | `docs/release/final_closure_certificate.md`, signed only at release. | [external] |
| NS-21 | H cleanup | Update `docs/project_status.md` by deleting/consolidating phantom Cluster H entries. | Single honest `Cluster H — Beta Release Governance` section linking evidence. | [ ] |

---

## 4. Prove database and migration runtime behavior

**Goal:** Move from local migration metadata to real database execution evidence.

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-22 | Run `alembic upgrade head` against disposable PostgreSQL. | `docs/release/migration_evidence.md` with full output. | [ ] |
| NS-23 | Run schema integrity check against disposable DB. | Captured output in migration evidence. | [ ] |
| NS-24 | Run downgrade/rollback path where supported. | Rollback evidence or documented non-downgrade rationale. | [ ] |

---

## 5. Prove frontend/browser behavior against backend

**Goal:** Replace opt-in/scaffold evidence with browser execution evidence.

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-25 | Run frontend coverage. | `docs/release/frontend_test_evidence.md`. | [ ] |
| NS-26 | Run Playwright/browser E2E against live local or staging backend. | Browser E2E output and environment details. | [ ] |
| NS-27 | Verify critical UI flows. | Evidence for login, dashboard, lesson generation, consent, POPIA export. | [ ] |
| NS-28 | Verify PWA/offline sync implementation status. | Either implemented endpoint evidence or explicit deferred scope entry. | [ ] |
| NS-29 | Verify parent dashboard implementation status. | Passing test/live evidence or explicit deferred scope entry. | [ ] |

---

## 6. Prove observability, backup, restore, rollback, and operator readiness

**Goal:** Convert operational docs into executed operational evidence.

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-30 | H-19 | Create operator runbook. | `docs/release/operator_runbook.md` with health, scale, rollback, escalation commands. | [ ] |
| NS-31 | H-20 | Configure uptime monitor for `GET /api/v2/health/deep`. | `docs/release/monitoring_evidence.md`. | [external] |
| NS-32 | H-21 | Wire Alertmanager to alert channel and fire test alert. | `docs/release/alertmanager_evidence.md`. | [external] |
| NS-33 | — | Execute backup dry-run. | Backup log with timestamp/checksum. | [ ] |
| NS-34 | — | Execute restore drill. | Restore log plus post-restore smoke test evidence. | [ ] |
| NS-35 | — | Execute rollback drill against staging or disposable environment. | Rollback evidence and runbook corrections. | [ ] |
| NS-36 | H-18 | Define change-control policy. | `docs/release/change_control_policy.md`. | [external] |
| NS-37 | — | Run incident tabletop. | `docs/release/incident_tabletop_evidence.md`. | [external] |

---

## 7. Complete POPIA, legal, security, and governance approvals

**Goal:** Separate engineering proof from required human/legal/security approvals.

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-38 | H-13 | Run POPIA sweep. | `docs/release/popia_sweep_evidence.md` with 0 issues or tracked exceptions. | [ ] |
| NS-39 | — | Submit POPIA docs for legal review. | Legal review record. | [external] |
| NS-40 | — | Obtain security review or pen-test decision. | Security sign-off or scoped finding report. | [external] |
| NS-41 | H-15 | Fill and sign sign-off manifest. | `docs/release/sign_off_manifest.md` with real names/dates/signatures. | [external] |
| NS-42 | H-16 | Create release decision log. | `docs/release/release_decision_log.md`. | [external] |

---

## 8. Resolve content/product readiness

**Goal:** Decide what beta can honestly include.

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-43 | Confirm current CAPS approved item count. | Item-bank report with approved vs candidate counts. | [ ] |
| NS-44 | Submit 106 AI-generated Grade 4 Maths candidates for educator review. | Review/sign-off records. | [external] |
| NS-45 | Reach or explicitly defer 120-item launch threshold. | Either approved 120-item evidence or beta-scope limitation document. | [ ] |
| NS-46 | Add independent answer-key validation plan. | Implementation or documented external review workflow. | [ ] |
| NS-47 | Define supported beta grades/subjects/languages. | Beta product scope document. | [ ] |
| NS-48 | Create known issues and limitations file. | `docs/release/known_issues.md`; must not be empty. | [ ] |
| NS-49 | Define beta acceptance criteria. | `docs/release/beta_acceptance_criteria.md` with actual metrics and thresholds. | [external] |

---

## 9. Implement or explicitly defer monetization and communications

**Goal:** Avoid pretending billing/notifications exist if they do not.

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-50 | Decide beta billing mode: free beta or paid beta. | Decision recorded in release bundle/product scope. | [ ] |
| NS-51 | If paid beta: implement Stripe/payment provider integration. | Checkout, webhook, subscription lifecycle, quota gating tests. | [ ] |
| NS-52 | If free beta: explicitly disable billing and document deferred monetization. | Feature flag/config + release note. | [ ] |
| NS-53 | Implement transactional notifications or defer. | Email/provider integration, templates, preferences, delivery logs, or deferred scope. | [ ] |
| NS-54 | Verify password reset / consent renewal / progress report communication path. | Tests or manual evidence. | [ ] |

---

## 10. Execute staging, beta readiness, and final go/no-go

**Goal:** Convert repository-local readiness into controlled launch evidence.

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-55 | — | Deploy to staging. | Staging deployment log. | [ ] |
| NS-56 | — | Run staging smoke tests. | Smoke output covering API, frontend, CORS, security headers. | [ ] |
| NS-57 | — | Verify staging telemetry and alerts. | Dashboard/alert evidence. | [ ] |
| NS-58 | H-22 | Create GitHub issue templates. | `.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`, `incorrect_content.md`, `popia_concern.md`. | [ ] |
| NS-59 | H-24 | Confirm beta exit criteria before launch. | `docs/release/beta_acceptance_criteria.md`. | [external] |
| NS-60 | — | Conduct formal beta go/no-go. | Signed release decision log. | [external] |
| NS-61 | H-25 | After beta ends, write beta outcome report. | `docs/release/beta_outcome_report.md`. | [post-beta] |
| NS-62 | H-26 | Sign final closure certificate only after evidence is complete. | Signed `docs/release/final_closure_certificate.md`. | [external] |
| NS-63 | — | Tag release candidate / beta release only after all required gates pass. | GitHub Release/tag with evidence bundle. | [external] |

---

## Completion summary

| Area | Status |
|---|---|
| Repository-side production-readiness baseline | [x] complete |
| Full local backend test baseline | [verify] one migration graph repair pending confirmation |
| CI on this fork | [ ] open |
| Branch protection | [external] open |
| Staging execution | [ ] open |
| Runtime DB migration proof | [ ] open |
| Backup/restore/rollback drill | [ ] open |
| Legal/security approval | [external] open |
| CAPS educator approval | [external] open |
| Billing/notifications decision | [ ] open |
| Controlled beta go/no-go | [external] open |
| Public beta / production launch | [ ] blocked |

---

## Rule for marking tasks complete

Do not mark an item `[x]` unless its evidence artefact can be opened and read.

Acceptable evidence includes:

- committed file path,
- passing CI URL,
- captured command output,
- signed review document,
- screenshot/settings export for external systems,
- staging/deployment logs,
- test result artefact.

A document that merely says “evidence added” is not evidence.
