"""content_factory_schema_contract.py — Single source of truth for the
Content Factory database schema contract.

All CI migration checks and unit tests MUST import their expected table names,
column names, and enum values from this module so that there is one place to
update when the schema evolves.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Required tables
# ---------------------------------------------------------------------------

REQUIRED_TABLES: list[str] = [
    "content_generation_artifacts",
    "content_artifact_sources",
    "content_generation_runs",
    "content_generation_tasks",
    "content_seed_runs",
    "content_staging_verification_runs",
    "content_staging_verification_scope_results",
    "content_promotion_events",
    "assessment_blueprints",
    "study_plan_templates",
    # Supporting tables
    "content_scopes",
    "content_coverage_targets",
    "content_validation_reports",
    "content_artifact_reviews",
    "content_review_assignments",
    "lesson_bank",
]

# ---------------------------------------------------------------------------
# Required columns per table  (table -> list[column_name])
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: dict[str, list[str]] = {
    "content_artifact_sources": [
        "source_document_id",
        "source_chunk_id",
        "license_status",
        "source_quality_score",
    ],
    "content_generation_tasks": [
        "idempotency_key",
        "depends_on_task_ids",
        "validation_failures",
        "token_usage",
    ],
    "content_generation_artifacts": [
        "artifact_id",
        "scope_id",
        "content_layer",
        "artifact_type",
        "status",
        "artifact_hash",
        "artifact_json",
    ],
    "content_generation_runs": [
        "run_id",
        "scope_id",
        "status",
        "requested_by",
        "run_metadata",
    ],
    "content_staging_verification_runs": [
        "run_id",
        "status",
        "summary_json",
        "created_by",
        "created_at",
        "completed_at",
    ],
    "content_staging_verification_scope_results": [
        "id",
        "run_id",
        "scope_id",
        "status",
        "can_seed_staging",
        "can_promote_production",
        "summary_json",
        "blockers_json",
    ],
    "content_review_assignments": [
        "id",
        "artifact_id",
        "assigned_to",
        "assigned_by",
        "assigned_at",
        "priority",
        "status",
        "resolved_at",
    ],
}

# ---------------------------------------------------------------------------
# Enum contracts  (pg_type_name -> list[expected_values])
# These are compared against the ORM enum definitions; the DB column may be
# stored as VARCHAR/TEXT when using native=False Alembic enums.
# ---------------------------------------------------------------------------

ENUM_CONTRACTS: dict[str, list[str]] = {
    "content_artifact_status": [
        "draft",
        "generated",
        "validation_failed",
        "pending_review",
        "approved",
        "seeded_staging",
        "promoted_production",
        "retired",
        "rejected",
        "quarantined",
        "generation_failed",
    ],
    "content_layer": [
        "diagnostic_items",
        "lessons",
        "assessment_blueprints",
        "study_plan_templates",
    ],
    "content_artifact_type": [
        "diagnostic_item",
        "lesson",
        "assessment_blueprint",
        "study_plan_template",
        "rubric",
        "remediation_path",
    ],
    "content_review_action": [
        "approve",
        "reject",
        "quarantine",
        "request_changes",
    ],
    "content_scope_status": [
        "draft",
        "active",
        "paused",
        "retired",
    ],
}

# ---------------------------------------------------------------------------
# ORM model → table name mapping
# Used by reconciliation tests to verify __tablename__ matches this contract.
# ---------------------------------------------------------------------------

ORM_TABLE_MAP: dict[str, str] = {
    "ContentGenerationArtifact": "content_generation_artifacts",
    "ContentArtifactSource": "content_artifact_sources",
    "ContentGenerationRun": "content_generation_runs",
    "ContentGenerationTask": "content_generation_tasks",
    "ContentSeedRun": "content_seed_runs",
    "ContentStagingVerificationRun": "content_staging_verification_runs",
    "ContentStagingVerificationScopeResult": "content_staging_verification_scope_results",
    "ContentPromotionEvent": "content_promotion_events",
    "AssessmentBlueprint": "assessment_blueprints",
    "StudyPlanTemplate": "study_plan_templates",
    "ContentScope": "content_scopes",
    "ContentCoverageTarget": "content_coverage_targets",
    "ContentValidationReport": "content_validation_reports",
    "ContentArtifactReview": "content_artifact_reviews",
    "ContentReviewAssignment": "content_review_assignments",
    "LessonBank": "lesson_bank",
}
