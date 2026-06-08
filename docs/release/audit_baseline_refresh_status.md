# Audit Baseline Refresh Status

Generated at: `2026-06-08T15:16:40Z`
Commit: `d8f1d702b13a2337b17e02f73b7edbabe91cf06f`
Branch: `fix/failing-tests`

**Status:** `audit-baseline-refresh-current`
**Beta decision:** `NO-GO`
**Beta blocker count:** `10`

## Commands

| Command | Return code |
|---|---:|
| `make final-gate-refresh` | 0 |
| `write release_go_no_go_status from final_beta_gate_refresh` | 0 |
| `python3 scripts/docs_inventory.py --write` | 0 |

## Status surfaces

| Surface | Exists | Status | Decision | Commit | Stale |
|---|---:|---|---|---|---:|
| `final_beta_gate_refresh` | True | `NO-GO` | `NO-GO` | `d8f1d702b13a2337b17e02f73b7edbabe91cf06f` | False |
| `release_go_no_go_status` | True | `NO-GO` | `NO-GO` | `d8f1d702b13a2337b17e02f73b7edbabe91cf06f` | False |
| `ci_evidence` | True | `ci-evidence-not-accepted` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `ci_run_evidence` | True | `external-blocked` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `external_approval` | True | `external-blocked` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `approval_evidence` | True | `external-blocked` | `` | `d8f1d702b13a2337b17e02f73b7edbabe91cf06f` | False |
| `staging_smoke_evidence` | True | `staging-smoke-evidence-not-accepted` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `staging_acceptance` | True | `external-blocked` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `auth_refresh_db_evidence` | True | `auth-refresh-db-evidence-accepted` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `popia_response_contract_no_skip` | True | `popia-response-contract-no-skip-passing` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `diag_deep_health_runtime` | True | `diag-deep-health-runtime-not-accepted` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `live_db_transaction_evidence` | True | `external-blocked` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `beta_blocker_burndown` | True | `` | `` | `431d83aeaa98b726e66612803618c0c0824a2fa8` | True |
| `docs_inventory` | True | `` | `` | `d8f1d702b13a2337b17e02f73b7edbabe91cf06f` | False |

## Accepted evidence marker preservation

| ID | Evidence file | Marker | Exists | Accepted marker present |
|---|---|---|---:|---:|
| `AUTH-REFRESH-DB-EVIDENCE-001` | `docs/release/auth_refresh_db_evidence_status.json` | `auth-refresh-db-evidence-accepted` | True | True |
| `POPIA-001` | `docs/release/popia_response_contract_no_skip_status.json` | `popia-response-contract-no-skip-passing` | True | True |
| `CI-001` | `docs/release/ci_evidence_status.json` | `ci-evidence-accepted` | True | False |
| `EVID-001` | `docs/release/ci_evidence_status.json` | `ci-evidence-accepted` | True | False |
| `STAGING-001` | `docs/release/staging_smoke_evidence_status.json` | `staging-smoke-evidence-accepted` | True | False |
| `DIAG-001` | `docs/release/diag_deep_health_runtime_status.json` | `diag-deep-health-runtime-accepted` | True | False |

## Remaining beta blockers

- `JWT-001`
- `ARQ-001`
- `POPIA-001`
- `CI-001`
- `LEGAL-001`
- `SEC-001`
- `CONTENT-001`
- `LESSON-AUTH-001`
- `STAGING-001`
- `EXT-GATE-001`

## Blockers

- None

## No false-closure rules

- This refresh does not close any blocker by itself.
- Accepted evidence is preserved but not fabricated.
- Missing external approval, frontend runtime, JWT, ARQ, lesson auth, scoring, transaction, and operations evidence remains blocking until separately proven.
- Beta remains NO-GO unless the final gate and registry genuinely clear all beta blockers.
