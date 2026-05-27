# Release State Snapshot

## Metadata

- generated_at_utc: `2026-05-26T20:31:01.490181+00:00`
- branch: `pr-cf-013-full-generation-runner`
- commit: `3fd35da07070e6f6e8bc43ec0915d25ba53da6a7`
- release_candidate: `unset`

## Working Tree Status

```text
M app/api_v2_routers/content_factory.py
 M app/domain/content_factory_schemas.py
 M docs/architecture/auth_boundary_debt_report.json
 M docs/architecture/auth_boundary_debt_report.md
 M docs/architecture/auth_service_extraction_followup.json
 M docs/architecture/auth_service_extraction_followup.md
 M docs/architecture/auth_service_extraction_report.json
 M docs/architecture/auth_service_extraction_report.md
 M docs/architecture/import_linter_availability.md
 M docs/architecture/import_linter_contract_run.md
 M docs/architecture/legacy_learner_access_guard_report.json
 M docs/architecture/legacy_learner_access_guard_report.md
 M docs/architecture/router_repository_boundary_matrix.json
 M docs/architecture/router_repository_boundary_matrix.md
 M docs/architecture/router_service_dependency_map.json
 M docs/architecture/router_service_dependency_map.md
 M docs/architecture/service_boundary_inventory.json
 M docs/architecture/service_boundary_inventory.md
 M docs/architecture/service_family_map.json
 M docs/architecture/service_family_map.md
 M docs/architecture/transaction_boundary_inventory.json
 M docs/architecture/transaction_boundary_inventory.md
 M docs/architecture/tx_route_wiring_inventory.json
 M docs/architecture/tx_route_wiring_inventory.md
 M docs/beta/beta_content_hard_gate.json
 M docs/beta/beta_content_hard_gate.md
 M docs/docs_gap_report.md
 M docs/docs_generation_plan.md
 M docs/docs_inventory.json
 M docs/docs_inventory.md
 M docs/operations/beta_release_evidence_bundle.md
 M docs/operations/beta_release_pr_body.md
 M docs/operations/beta_signoff_manifest.md
 M docs/operations/database_backup_manifest.md
 M docs/operations/database_restore_evidence.md
 M docs/operations/release_candidate_tag_manifest.md
 M docs/operations/release_evidence_manifest.md
 M docs/operations/release_state_snapshot.md
 M docs/operations/staging_smoke_evidence_manifest.md
 M docs/release/alertmanager_drill_evidence.json
 M docs/release/approval_evidence_status.json
 M docs/release/approval_evidence_status.md
 M docs/release/audit_baseline_refresh_status.json
 M docs/release/audit_baseline_refresh_status.md
 M docs/release/auth_db_lifecycle_proof_report.json
 M docs/release/auth_db_lifecycle_proof_report.md
 M docs/release/auth_http_success_scope_report.json
 M docs/release/auth_http_success_scope_report.md
 M docs/release/auth_lifecycle_http_proof_status.json
 M docs/release/auth_lifecycle_http_proof_status.md
 M docs/release/auth_lifecycle_semantic_proof_status.json
 M docs/release/auth_lifecycle_semantic_proof_status.md
 M docs/release/auth_refresh_db_evidence_status.json
 M docs/release/auth_refresh_db_evidence_status.md
 M docs/release/auth_route_logout_delegate_status.json
 M docs/release/auth_route_logout_delegate_status.md
 M docs/release/auth_route_service_dependency_repair_status.json
 M docs/release/auth_route_service_dependency_repair_status.md
 M docs/release/auth_route_transaction_slice_report.json
 M docs/release/auth_route_transaction_slice_report.md
 M docs/release/auth_router_boundary_introspection.json
 M docs/release/auth_router_boundary_introspection.md
 M docs/release/auth_service_cleanup_status.json
 M docs/release/auth_service_cleanup_status.md
 M docs/release/auth_service_extraction_repair_report.md
 M docs/release/backend_consolidation_diagnostic_report.md
 M docs/release/backend_consolidation_evidence_manifest.md
 M docs/release/backend_consolidation_execution_report.md
 M docs/release/backend_consolidation_implementation_foundation_report.md
 M docs/release/backend_consolidation_progress_report.md
 M docs/release/backend_consolidation_readiness_report.md
 M docs/release/backend_consolidation_terminal_report.md
 M docs/release/backend_deletion_candidate_inventory.md
 M docs/release/backend_first_wiring_candidates_report.md
 M docs/release/backend_implementation_371_375_report.md
 M docs/release/backend_runtime_compatibility_report.md
 M docs/release/backend_runtime_enablement_report.md
 M docs/release/backend_runtime_integration_readiness_report.md
 M docs/release/backend_runtime_probe_report.md
 M docs/release/backend_runtime_wiring_cases_report.md
 M docs/release/backend_runtime_wiring_preflight_report.md
 M docs/release/backup_drill_evidence.json
 M docs/release/backup_drill_evidence.md
 M docs/release/beta_blocker_burndown_plan.json
 M docs/release/beta_blocker_burndown_plan.md
 M docs/release/beta_evidence_integrity_repair_report.json
 M docs/release/beta_evidence_integrity_repair_report.md
 M docs/release/beta_no_go_handoff_packet.json
 M docs/release/beta_no_go_handoff_packet.md
 M docs/release/beta_readiness_status.json
 M docs/release/branch_protection_evidence.json
 M docs/release/branch_protection_evidence.md
 M docs/release/ci_auth_refresh_db_proof_workflow_status.json
 M docs/release/ci_auth_refresh_db_proof_workflow_status.md
 M docs/release/ci_authority_status.json
 M docs/release/ci_authority_status.md
 M docs/release/ci_evidence.json
 M docs/release/ci_evidence_status.json
 M docs/release/ci_evidence_status.md
 M docs/release/ci_run_evidence_status.json
 M docs/release/ci_run_evidence_status.md
 M docs/release/db_live_only_table_ownership_status.json
 M docs/release/db_live_only_table_ownership_status.md
 M docs/release/db_migration_seed_repeatability_status.json
 M docs/release/db_migration_seed_repeatability_status.md
 M docs/release/diag_deep_health_runtime_status.json
 M docs/release/diag_deep_health_runtime_status.md
 M docs/release/diagnostic_item_bank_canonicality_status.json
 M docs/release/diagnostic_item_bank_canonicality_status.md
 M docs/release/diagnostics_db_integrity_proof.json
 M docs/release/diagnostics_db_integrity_proof.md
 M docs/release/diagnostics_route_transaction_gap_plan.json
 M docs/release/diagnostics_route_transaction_gap_plan.md
 M docs/release/diagnostics_route_transaction_slice_report.json
 M docs/release/diagnostics_route_transaction_slice_report.md
 M docs/release/disposable_db_schema_proof_execution_report.md
 M docs/release/evidence_attachment_runbook.md
 M docs/release/evidence_attachment_runbook_manifest.json
 M docs/release/evidence_status_registry.yml
 M docs/release/external_approval_status.json
 M docs/release/external_approval_status.md
 M docs/release/final_beta_gate_refresh.json
 M docs/release/final_beta_gate_refresh.md
 M docs/release/first_audit_runtime_wiring_report.md
 M docs/release/live_db_transaction_evidence_status.json
 M docs/release/live_db_transaction_evidence_status.md
 M docs/release/popia_lifecycle_runtime_proof.json
 M docs/release/popia_lifecycle_runtime_proof.md
 M docs/release/popia_response_contract_no_skip_status.json
 M docs/release/popia_response_contract_no_skip_status.md
 M docs/release/popia_route_transaction_gap_plan.json
 M docs/release/popia_route_transaction_gap_plan.md
 M docs/release/popia_route_transaction_slice_report.json
 M docs/release/popia_route_transaction_slice_report.md
 M docs/release/production_frontend_deployment_status.json
 M docs/release/production_frontend_deployment_status.md
 M docs/release/production_frontend_runtime_status.json
 M docs/release/production_frontend_runtime_status.md
 M docs/release/release_go_no_go_status.json
 M docs/release/release_go_no_go_status.md
 M docs/release/release_owner_beta_go_no_go_memo.md
 M docs/release/restore_drill_evidence.json
 M docs/release/rollback_drill_evidence.json
 M docs/release/route_transaction_implementation_plan.json
 M docs/release/route_transaction_implementation_plan.md
 M docs/release/route_transaction_slice_rollup.json
 M docs/release/route_transaction_slice_rollup.md
 M docs/release/runtime_wiring_431_450_report.md
 M docs/release/schema_drift_disposable_latest.json
 M docs/release/schema_drift_disposable_latest.md
 M docs/release/staging_acceptance_status.json
 M docs/release/staging_acceptance_status.md
 M docs/release/staging_smoke_evidence.md
 M docs/release/staging_smoke_evidence_status.json
 M docs/release/staging_smoke_evidence_status.md
 M docs/release/staging_smoke_final_evidence.json
 M docs/release/staging_smoke_final_evidence.md
 M docs/release/staging_smoke_workflow_status.json
 M docs/release/staging_smoke_workflow_status.md
 M docs/release/transaction_rollback_rollup_report.json
 M docs/release/transaction_rollback_rollup_report.md
 M docs/security/dependency_pin_report.json
 M docs/security/dependency_pin_report.md
 M docs/security/jwt_rotation_introspection.json
 M docs/security/jwt_rotation_introspection.md
 M docs/security/jwt_rotation_repair_report.md
 M package.json
 M pytest.ini
 M scripts/check_auth_refresh_db_proof.py
 M scripts/check_final_gate_refresh.py
 M scripts/check_popia_response_contract_no_skips.py
 M scripts/check_prod_frontend_deployment.py
 M scripts/check_prod_frontend_runtime.py
 M scripts/popia_response_contract_no_skips.py
?? docs/content_factory_overnight_batch_pipeline.md
?? docs/input/
?? reports/content_factory/full_generation/20260526_174919/review_bundles/
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
