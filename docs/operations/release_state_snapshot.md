# Release State Snapshot

## Metadata

- generated_at_utc: `2026-05-15T18:58:09.195188+00:00`
- branch: `codex/production_readiness`
- commit: `0bac413d3f09cb144fd6b8674f770e725ddc282f`
- release_candidate: `unset`

## Working Tree Status

```text
D app/api/__init__.py
 D app/api/main.py
 M app/api_v2_routers/audit.py
 M app/api_v2_routers/popia.py
 M app/models/__init__.py
 M app/modules/lessons/lesson_schema_v1.py
 M app/repositories/audit_repository.py
 M app/services/popia_service.py
 M docs/operations/beta_release_evidence_bundle.md
 M docs/operations/beta_release_pr_body.md
 M docs/operations/beta_signoff_manifest.md
 M docs/operations/database_backup_manifest.md
 M docs/operations/database_restore_evidence.md
 M docs/operations/release_candidate_tag_manifest.md
 M docs/operations/release_evidence_manifest.md
 M docs/operations/release_state_snapshot.md
 M docs/operations/staging_smoke_evidence_manifest.md
 M docs/security/PHASE2_AUTHORIZATION_CLOSURE.md
 M docs/security/popia_consent_boundary_matrix.md
 D docs/security/popia_deletion_execute_authorization_wiring.md
 D docs/security/popia_deletion_status_authorization_wiring.md
 M scripts/check_phase2_authorization_evidence.py
 M scripts/check_popia_consent_audit_evidence.py
 M scripts/check_popia_consent_boundary_matrix.py
 M scripts/check_runtime_entrypoints.py
 M scripts/generate_popia_consent_boundary_matrix.py
 M scripts/validate_schema_integrity.py
 M tests/conftest.py
 D tests/integration/test_popia_correction_request_authorization.py
 D tests/integration/test_popia_data_export_authorization.py
 D tests/integration/test_popia_deletion_cancel_authorization.py
 D tests/integration/test_popia_deletion_execute_authorization.py
 D tests/integration/test_popia_deletion_request_authorization.py
 D tests/integration/test_popia_deletion_status_authorization.py
 D tests/integration/test_popia_restriction_request_authorization.py
 M tests/integration/test_v2_jobs.py
 M tests/popia/test_consent_audit_trail.py
 M tests/smoke/test_v2_smoke.py
 M tests/test_popia_end_to_end.py
 M tests/test_popia_negative.py
 M tests/unit/modules/diagnostics/test_item_bank_pipeline.py
 M tests/unit/test_generate_popia_consent_boundary_matrix.py
 M tests/unit/test_popia_correction_request_authorization_wiring.py
 M tests/unit/test_popia_data_export_authorization_wiring.py
 M tests/unit/test_popia_data_rights_consent_boundary.py
 M tests/unit/test_popia_deletion_cancel_authorization_wiring.py
 D tests/unit/test_popia_deletion_execute_authorization_wiring.py
 M tests/unit/test_popia_deletion_request_authorization_wiring.py
 D tests/unit/test_popia_deletion_status_authorization_wiring.py
 M tests/unit/test_popia_restriction_request_authorization_wiring.py
 M tests/unit/test_popia_service.py
?? docs/release/full_pytest_latest.txt
?? docs/release/full_pytest_latest_v2.txt
?? docs/release/integration_full_latest.txt
```

## State Artifacts

| Artifact | Present |
| --- | --- |
| `docs/operations/beta_release_readiness_contract.md` | `yes` |
| `docs/operations/beta_release_evidence_bundle.md` | `yes` |
| `docs/operations/beta_release_final_checklist.md` | `yes` |
| `docs/operations/beta_release_execution_plan.md` | `yes` |
| `docs/operations/beta_release_pr_body.md` | `yes` |
| `docs/operations/final_release_verification_bundle.md` | `yes` |
| `docs/operations/project_release_closure_index.md` | `yes` |
| `docs/operations/CLUSTER_H_CLOSURE.md` | `yes` |
| `PR_INTEGRATION_SUMMARY.md` | `yes` |
| `docs/project_status.md` | `yes` |

## Snapshot Boundary

This release state snapshot records local repository state at generation time.
It does not replace CI logs, platform approvals, or release tag history.

## Command

```bash
make release-state-snapshot
```
