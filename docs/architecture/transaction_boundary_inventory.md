# Transaction Boundary Inventory

Generated at: `2026-06-01T14:41:24Z`

Candidate count: `276`
Critical candidate count: `52`

Policy: Multi-write candidates remain not-proven until rollback/integration tests demonstrate atomicity.

| File | Function | Line | Status | Critical areas | Mutation calls | Transaction markers |
|---|---|---:|---|---|---|---|
| `app/api_v2_routers/0005_irt_seed.py` | `downgrade` | 225 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `_invalidate_existing_tokens` | 188 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `_create_secure_token` | 206 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/api_v2_routers/auth_extended.py` | `_consume_token` | 226 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `forgot_password` | 259 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `reset_password` | 295 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/auth_extended.py` | `send_verification` | 315 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/auth_extended.py` | `verify_email` | 345 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `get_onboarding` | 386 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `update_onboarding_step` | 407 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `update_learner_profile` | 447 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `get_privacy_settings` | 497 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `update_privacy_settings` | 515 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `request_data_export` | 539 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/auth_extended.py` | `request_account_deletion` | 566 | `multi-write-candidate-not-proven` | `-` | `add, commit, execute` | `-` |
| `app/api_v2_routers/consent.py` | `grant_consent` | 39 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `grant` | `-` |
| `app/api_v2_routers/consent.py` | `revoke_consent` | 72 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `revoke` | `-` |
| `app/api_v2_routers/content_factory.py` | `create_generation_run` | 262 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `plan_missing_generation_tasks` | 306 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `execute_generation_run` | 321 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `execute_generation_task` | 339 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `cancel_generation_run` | 379 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `retry_failed_generation_tasks` | 394 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `list_artifacts` | 406 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/content_factory.py` | `submit_artifact_for_review` | 463 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `approve_artifact` | 473 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `reject_artifact` | 483 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `quarantine_artifact` | 490 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `assign_reviewer` | 545 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `bulk_assign_reviewer` | 560 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `bulk_approve_review` | 592 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `bulk_reject_review` | 607 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `bulk_quarantine_review` | 622 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `run_all_scope_staging_verification` | 637 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `seed_scope_staging` | 736 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `rollback_seed_run` | 811 | `transaction-marker-present` | `-` | `commit` | `rollback` |
| `app/api_v2_routers/content_factory.py` | `promote_production` | 875 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/api_v2_routers/content_factory.py` | `get_promotion_event_items` | 932 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/content_factory.py` | `rollback_promotion_event` | 981 | `transaction-marker-present` | `-` | `commit` | `rollback` |
| `app/api_v2_routers/content_factory.py` | `get_content_factory_report` | 1018 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/content_factory.py` | `plan_full_generation` | 1098 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/api_v2_routers/content_factory.py` | `start_full_generation` | 1132 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/api_v2_routers/content_factory.py` | `list_full_generation_runs` | 1167 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/content_factory.py` | `cancel_full_generation_run` | 1226 | `multi-write-candidate-not-proven` | `-` | `execute, flush` | `-` |
| `app/api_v2_routers/content_factory.py` | `resume_full_generation_run` | 1261 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/api_v2_routers/diagnostics.py` | `submit_diagnostic` | 102 | `multi-write-candidate-not-proven` | `diagnostics_response` | `upsert` | `-` |
| `app/api_v2_routers/gamification.py` | `award_xp` | 46 | `multi-write-candidate-not-proven` | `lesson_completion` | `commit` | `-` |
| `app/api_v2_routers/learners.py` | `create_learner` | 25 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/api_v2_routers/learners.py` | `request_erasure` | 123 | `single-mutation-candidate` | `-` | `delete` | `-` |
| `app/api_v2_routers/parents.py` | `get_parent_trust_dashboard` | 105 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/api_v2_routers/parents.py` | `get_learner_progress` | 219 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/parents.py` | `request_erasure` | 271 | `single-mutation-candidate` | `-` | `delete` | `-` |
| `app/api_v2_routers/popia.py` | `grant_consent` | 102 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `grant` | `-` |
| `app/api_v2_routers/popia.py` | `deny_consent` | 119 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `deny` | `-` |
| `app/api_v2_routers/popia.py` | `withdraw_consent` | 137 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `withdraw` | `-` |
| `app/api_v2_routers/popia.py` | `renew_consent` | 152 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `renew` | `-` |
| `app/modules/auth/service.py` | `register_guardian` | 66 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/modules/auth/service.py` | `authenticate` | 136 | `multi-write-candidate-not-proven` | `auth_refresh` | `update` | `-` |
| `app/modules/auth/service.py` | `verify_email` | 200 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/modules/billing/production_readiness_contracts.py` | `process` | 239 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/modules/consent/service.py` | `grant` | 165 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `grant` | `-` |
| `app/modules/consent/service.py` | `revoke` | 217 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `revoke` | `-` |
| `app/modules/consent/service.py` | `renew` | 252 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `renew` | `-` |
| `app/modules/consent/service.py` | `execute_erasure` | 300 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `revoke` | `-` |
| `app/modules/consent/service.py` | `_record_version_history` | 397 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `add, flush` | `-` |
| `app/modules/diagnostics/irt_engine.py` | `record_response` | 595 | `multi-write-candidate-not-proven` | `diagnostics_response` | `add` | `-` |
| `app/modules/diagnostics/item_generator.py` | `_call_llm_for_json` | 224 | `single-mutation-candidate` | `-` | `complete` | `-` |
| `app/modules/diagnostics/item_validator.py` | `__init__` | 136 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/modules/diagnostics/item_validator.py` | `_index_topic_list` | 151 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/modules/diagnostics/service.py` | `grant_consent` | 46 | `transaction-marker-present` | `popia_lifecycle` | `grant` | `atomic, transaction` |
| `app/modules/diagnostics/service.py` | `revoke_consent` | 107 | `transaction-marker-present` | `popia_lifecycle` | `revoke` | `transaction` |
| `app/modules/diagnostics/session_recovery_service.py` | `invalidate_session_snapshot` | 69 | `single-mutation-candidate` | `-` | `delete` | `-` |
| `app/modules/jobs.py` | `expire_stale_diagnostic_sessions` | 85 | `multi-write-candidate-not-proven` | `-` | `commit, execute, update` | `-` |
| `app/modules/lessons/answer_key_verifier.py` | `verify` | 167 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/budget_guardrails.py` | `add` | 101 | `transaction-marker-present` | `lesson_completion` | `execute` | `atomic` |
| `app/modules/lessons/budget_guardrails.py` | `record_usage` | 219 | `multi-write-candidate-not-proven` | `lesson_completion` | `add` | `-` |
| `app/modules/lessons/caps_topic_map_service.py` | `load_maps` | 161 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/modules/lessons/lesson_generator.py` | `generate` | 118 | `multi-write-candidate-not-proven` | `lesson_completion` | `commit` | `-` |
| `app/modules/lessons/llm_gateway.py` | `generate` | 65 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/llm_gateway.py` | `_call_groq` | 129 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/modules/lessons/llm_gateway.py` | `_call_anthropic` | 183 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/modules/lessons/llm_gateway_v2.py` | `complete` | 144 | `multi-write-candidate-not-proven` | `lesson_completion` | `create` | `-` |
| `app/modules/lessons/llm_gateway_v2.py` | `complete` | 200 | `multi-write-candidate-not-proven` | `lesson_completion` | `create` | `-` |
| `app/modules/lessons/llm_gateway_v2.py` | `complete` | 292 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/parent_explanation_mode.py` | `generate_parent_summary` | 222 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/service.py` | `generate_lesson_for_learner` | 86 | `multi-write-candidate-not-proven` | `-` | `commit, create` | `-` |
| `app/modules/lessons/service.py` | `complete_lesson` | 190 | `multi-write-candidate-not-proven` | `lesson_completion` | `commit` | `-` |
| `app/modules/lessons/service.py` | `record_feedback` | 199 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/modules/lessons/service.py` | `get_lesson_by_id` | 209 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/modules/lessons/service.py` | `_build_learner_context` | 221 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/modules/lessons/teacher_insight_mode.py` | `generate_teacher_insight` | 319 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/notifications/production_readiness_contracts.py` | `enqueue` | 256 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/audit_migration_orchestrator.py` | `build_audit_migration_event` | 40 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `_create_schema` | 44 | `multi-write-candidate-not-proven` | `auth_refresh` | `commit` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `register` | 81 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `login` | 114 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `refresh` | 129 | `multi-write-candidate-not-proven` | `auth_refresh` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `learner_ids_for_guardian` | 141 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `_issue_tokens` | 148 | `multi-write-candidate-not-proven` | `auth_refresh` | `execute` | `-` |
| `app/services/auth_lifecycle_impl.py` | `create_dev_session_impl` | 58 | `multi-write-candidate-not-proven` | `auth_refresh` | `create` | `-` |
| `app/services/auth_lifecycle_impl.py` | `register_impl` | 208 | `multi-write-candidate-not-proven` | `auth_refresh` | `create` | `-` |
| `app/services/auth_service.py` | `guardian_signup` | 147 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/auth_transactional_registration.py` | `register` | 55 | `transaction-marker-present` | `-` | `execute` | `begin, transaction` |
| `app/services/consent_compat.py` | `normalize_consent_audit_event` | 48 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/consent_renewal_service.py` | `_fetch_expiring_consents` | 276 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `execute` | `-` |
| `app/services/consent_renewal_service.py` | `_fetch_guardian` | 299 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `execute` | `-` |
| `app/services/consent_runtime_compatibility.py` | `normalize_consent_runtime_operation` | 110 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `update` | `-` |
| `app/services/consent_service.py` | `grant` | 42 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `create, grant, update` | `-` |
| `app/services/consent_service.py` | `deny` | 83 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `create, deny, update` | `-` |
| `app/services/consent_service.py` | `withdraw` | 115 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `update, withdraw` | `-` |
| `app/services/consent_service.py` | `renew` | 135 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `renew, update` | `-` |
| `app/services/consent_service.py` | `process_expiry` | 159 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/consent_service.py` | `flag_approaching_renewals` | 192 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `update` | `-` |
| `app/services/content_artifact_lifecycle.py` | `submit_for_review` | 33 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_artifact_lifecycle.py` | `approve_artifact` | 46 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_artifact_lifecycle.py` | `quarantine_artifact` | 62 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_artifact_lifecycle.py` | `mark_seeded_staging` | 79 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_artifact_lifecycle.py` | `mark_promoted_production` | 88 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_artifact_lifecycle.py` | `_set_status` | 97 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_factory.py` | `create_artifact` | 170 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_factory.py` | `validate_existing_artifact` | 242 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_factory.py` | `review_artifact` | 276 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_factory.py` | `_get_artifact` | 341 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_generation/blueprint_generator.py` | `generate` | 24 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_generation/source_context.py` | `build_context` | 27 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_generation/study_plan_template_generator.py` | `generate` | 24 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_generation_executor.py` | `execute_task` | 68 | `transaction-marker-present` | `-` | `add, flush` | `begin` |
| `app/services/content_generation_executor.py` | `execute_run` | 150 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_generation_executor.py` | `_existing_hashes` | 234 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_generation_executor.py` | `_fail_task` | 238 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_generation_planner.py` | `plan_missing_for_run` | 49 | `multi-write-candidate-not-proven` | `-` | `add, execute, flush` | `-` |
| `app/services/content_generation_run_lock.py` | `acquire` | 36 | `multi-write-candidate-not-proven` | `-` | `add, execute, flush` | `-` |
| `app/services/content_generation_run_lock.py` | `release` | 122 | `multi-write-candidate-not-proven` | `-` | `execute, flush` | `-` |
| `app/services/content_generation_run_lock.py` | `_get_active_lock` | 164 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_generation_run_lock.py` | `_release_stale_locks` | 186 | `multi-write-candidate-not-proven` | `-` | `execute, flush` | `-` |
| `app/services/content_generation_runs.py` | `create_run` | 22 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_generation_runs.py` | `list_runs` | 41 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_generation_runs.py` | `create_tasks_for_run` | 48 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_generation_runs.py` | `get_run_tasks` | 73 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_generation_runs.py` | `mark_task_running` | 80 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_generation_runs.py` | `mark_task_succeeded` | 86 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_generation_runs.py` | `mark_task_failed` | 93 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_generation_runs.py` | `cancel_run` | 100 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_generation_runs.py` | `retry_failed_tasks` | 110 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_generation_runs.py` | `_mark_task` | 133 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_learner_read_service.py` | `get_diagnostic_items` | 135 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_learner_read_service.py` | `get_lessons` | 211 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_promotion_executor.py` | `dry_run_promotion` | 66 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_promotion_executor.py` | `promote_scope` | 104 | `multi-write-candidate-not-proven` | `-` | `add, execute, flush` | `-` |
| `app/services/content_production_promotion_executor.py` | `get_promotion_event` | 214 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_promotion_executor.py` | `list_promotion_events` | 249 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_promotion_executor.py` | `rollback_promotion` | 304 | `transaction-marker-present` | `-` | `execute, flush` | `rollback` |
| `app/services/content_production_promotion_gate.py` | `_check_staging_verification` | 157 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_promotion_gate.py` | `_check_artifact_status` | 225 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_read_verification.py` | `verify_promotion_event` | 35 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_production_read_verification.py` | `verify_scope_production` | 109 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_review_queue.py` | `list_queue` | 75 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_review_queue.py` | `_load_assignments` | 146 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_review_queue.py` | `_latest_validation_reports` | 152 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_reviewer_assignment.py` | `assign_artifact` | 28 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_reviewer_assignment.py` | `unassign_artifact` | 75 | `single-mutation-candidate` | `-` | `flush` | `-` |
| `app/services/content_reviewer_assignment.py` | `get_reviewer_workload` | 84 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_reviewer_assignment.py` | `list_assignments` | 96 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_reviewer_assignment.py` | `_open_assignment` | 105 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_scope_registry.py` | `_load_topic_map_refs` | 105 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/content_seed_promotion.py` | `dry_run_seed` | 38 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_seed_promotion.py` | `seed_staging` | 51 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_staging_preview_service.py` | `preview_scope` | 75 | `multi-write-candidate-not-proven` | `-` | `add, execute` | `-` |
| `app/services/content_staging_preview_service.py` | `preview_caps_ref` | 159 | `multi-write-candidate-not-proven` | `-` | `add, execute` | `-` |
| `app/services/content_staging_read_verification.py` | `verify_seed_run` | 35 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_read_verification.py` | `verify_scope_staging` | 93 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_readiness.py` | `persist_report` | 203 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/content_staging_readiness.py` | `list_runs` | 236 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_readiness.py` | `get_run_report` | 240 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_readiness.py` | `_load_scope_artifacts` | 275 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_readiness.py` | `_load_source_index` | 279 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_seed_executor.py` | `seed_staging` | 97 | `transaction-marker-present` | `-` | `add, flush` | `rollback` |
| `app/services/content_staging_seed_executor.py` | `list_seed_runs` | 204 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_seed_executor.py` | `list_seed_run_items` | 227 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/content_staging_seed_executor.py` | `rollback_seed_run` | 252 | `transaction-marker-present` | `-` | `execute, flush` | `rollback` |
| `app/services/content_staging_seed_executor.py` | `_plan_seed` | 289 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `create_export_request` | 55 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `build_and_complete_export` | 89 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `create_erasure_request` | 137 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `approve_erasure` | 166 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `execute_erasure` | 187 | `transaction-marker-present` | `lesson_completion` | `execute` | `transaction` |
| `app/services/data_subject_rights_service.py` | `create_correction_request` | 262 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `complete_correction` | 290 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `create_restriction_request` | 309 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `lift_restriction` | 331 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/deep_readiness_runtime.py` | `_execute` | 19 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/diagnostic_data_integrity.py` | `extract_diagnostic_item_ids` | 20 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_data_integrity.py` | `walk` | 25 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_data_integrity.py` | `validate_diagnostic_submission_payload` | 62 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_session_integrity.py` | `served_item_ids` | 42 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_transactional_response.py` | `submit_response` | 60 | `transaction-marker-present` | `diagnostics_response` | `execute` | `begin, transaction` |
| `app/services/etl/etl_pipeline.py` | `_sha256` | 294 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/etl/etl_pipeline.py` | `init_db` | 1007 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/services/etl/etl_pipeline.py` | `ingest` | 1021 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `extract` | 1083 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `normalize` | 1111 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `chunk` | 1144 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `validate` | 1177 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `approve_document` | 1222 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `reject_document` | 1234 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `reprocess_document` | 1246 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `list_documents` | 1256 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `get_review_queue` | 1273 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `get_pipeline_stats` | 1281 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `get_content_gaps` | 1299 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `get_quality_report` | 1307 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `_save_document` | 1319 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `_load_document` | 1333 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `_load_chunks` | 1355 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `_log_job` | 1362 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline.py` | `_create_review_task` | 1369 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `init_db` | 294 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `init_fts` | 308 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `_populate_fts` | 329 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `create_version` | 348 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `_list_versions` | 385 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `add_curriculum_mapping` | 403 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `update_document_metadata` | 417 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `deprecate_document` | 446 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `index_chunk_for_search` | 461 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `search_fulltext` | 476 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `store_embedding` | 553 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `semantic_search_stub` | 586 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `hybrid_search` | 635 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `mark_indexed` | 673 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `generate_training_dataset` | 687 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `list_training_datasets` | 819 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `get_training_examples` | 825 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `contamination_check` | 834 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `_hashes` | 837 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `export_dataset` | 855 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `mark_training_ready` | 913 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `record_metric` | 928 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `submit_feedback` | 936 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `get_stale_documents` | 980 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `get_feedback_summary` | 1000 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `get_job_failure_rate` | 1009 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `get_monitoring_report` | 1025 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v2.py` | `get_completeness_report` | 1081 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `init_db` | 182 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `_record_audit` | 191 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `get_audit_trail` | 215 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `deprecate_document` | 228 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `update_metadata_with_audit` | 271 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `assign_reviewer` | 357 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `get_reviewer_workload` | 387 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `split_dataset` | 400 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `_make_child` | 438 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `check_contamination` | 480 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `get_dataset_statistics` | 531 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `resolve_feedback` | 583 | `multi-write-candidate-not-proven` | `-` | `commit, execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `get_metric_window` | 614 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/etl/etl_pipeline_v3_additions.py` | `get_completeness_trend` | 643 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/job_runtime_integrity.py` | `assert_no_runtime_objects` | 29 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/job_runtime_integrity.py` | `walk` | 32 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/launch_content_seed.py` | `seed_launch_content_if_needed` | 38 | `transaction-marker-present` | `lesson_completion` | `commit` | `rollback` |
| `app/services/launch_content_seed.py` | `_try_advisory_lock` | 98 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/launch_content_seed.py` | `_release_advisory_lock` | 108 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/launch_content_seed.py` | `_approved_item_counts` | 120 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/launch_content_seed.py` | `_approved_lesson_counts` | 132 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/launch_content_seed.py` | `_seed_items` | 141 | `single-mutation-candidate` | `-` | `upsert` | `-` |
| `app/services/launch_content_seed.py` | `_seed_lessons` | 150 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/launch_content_seed.py` | `_seed_learner_id` | 171 | `multi-write-candidate-not-proven` | `-` | `add, execute, flush` | `-` |
| `app/services/lesson_authorization.py` | `lesson_owner_learner_id` | 105 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/services/lesson_authorization.py` | `iter_sync_lesson_ids` | 162 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/lesson_authorization.py` | `walk` | 166 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/lesson_service_v2.py` | `generate_lesson` | 29 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/lesson_transactional_completion.py` | `complete_lesson` | 54 | `transaction-marker-present` | `lesson_completion` | `execute, update` | `begin, transaction` |
| `app/services/llm/gateway.py` | `complete` | 140 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/services/llm/json_completion.py` | `complete_json` | 72 | `single-mutation-candidate` | `-` | `complete` | `-` |
| `app/services/llm/json_completion.py` | `_call_groq` | 124 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/llm/json_completion.py` | `_call_anthropic` | 155 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/pii_sweep.py` | `scan_record` | 132 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_sa_id` | 163 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_email` | 175 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_phone_regex` | 185 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_phone_lib` | 195 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_salutation` | 209 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/popia_service.py` | `request_erasure` | 137 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `add, flush` | `-` |
| `app/services/popia_service.py` | `cancel_erasure` | 213 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/popia_service.py` | `request_correction` | 263 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/popia_service.py` | `restrict_processing` | 290 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `flush, revoke` | `-` |
| `app/services/popia_service.py` | `execute_erasure` | 329 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/study_plan_service_v2.py` | `generate_plan` | 15 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/study_plan_service_v2.py` | `_weak_caps_refs` | 76 | `single-mutation-candidate` | `-` | `add` | `-` |
