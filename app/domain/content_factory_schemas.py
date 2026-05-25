"""Pydantic schemas for Content Factory admin routes."""
from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.content_factory import ContentArtifactType, ContentLayer, ContentReviewAction


class ETLSourceCitation(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_document_id: str
    source_chunk_id: str | None = None
    curriculum_mapping_id: str | None = None
    source_hash: str | None = None
    source_role: str = "primary_context"
    caps_ref: str | None = None
    document_status: str | None = None
    license_status: str | None = None
    chunk_quality_score: float | None = None


class SourceBundleValidationRequest(BaseModel):
    caps_ref: str | None = None
    min_sources: int = Field(default=1, ge=0, le=20)
    require_approved_documents: bool = True
    allow_synthetic_without_source: bool = False
    sources: list[ETLSourceCitation] = Field(default_factory=list)


class SourceBundleValidationResponse(BaseModel):
    passed: bool
    errors: list[str]
    source_snapshot_hash: str | None


class ContentFactoryHealthResponse(BaseModel):
    status: str
    route_scope: str
    generation_enabled: bool = False


class ContentFactoryETLStatusResponse(BaseModel):
    status: str
    pipeline_package: str
    mcp_runtime_imported: bool
    notes: list[str] = Field(default_factory=list)


class ContentArtifactCreate(BaseModel):
    scope_id: str
    content_layer: ContentLayer
    artifact_type: ContentArtifactType
    artifact_json: dict[str, Any]
    caps_ref: str | None = None
    grade: int | None = Field(default=None, ge=0, le=12)
    subject_code: str | None = None
    language: str | None = "en"
    schema_version: str = "1.0"
    provider: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    token_usage: dict[str, Any] | None = None
    cost_metadata: dict[str, Any] | None = None
    quality_score: float | None = Field(default=None, ge=0, le=1)
    safety_status: str | None = "passed"
    answer_key_verified: bool = False
    caps_alignment_score: float | None = Field(default=None, ge=0, le=1)
    min_sources: int = Field(default=1, ge=0, le=20)
    sources: list[ETLSourceCitation] = Field(default_factory=list)


class ContentArtifactValidationRequest(BaseModel):
    artifact_type: ContentArtifactType
    artifact_json: dict[str, Any]
    caps_ref: str | None = None
    min_sources: int = Field(default=1, ge=0, le=20)
    sources: list[ETLSourceCitation] = Field(default_factory=list)


class ContentArtifactResponse(BaseModel):
    artifact_id: uuid.UUID
    scope_id: str
    content_layer: str
    artifact_type: str
    caps_ref: str | None
    status: str
    artifact_hash: str
    source_snapshot_hash: str | None


class ContentValidationReportResponse(BaseModel):
    validation_report_id: uuid.UUID
    artifact_id: uuid.UUID
    passed: bool
    checks: dict[str, Any]
    errors: list[str]


class ContentArtifactValidationResponse(BaseModel):
    passed: bool
    checks: dict[str, Any]
    errors: list[str]
    source_snapshot_hash: str | None


class ContentArtifactProvenanceSourceResponse(BaseModel):
    source_document_id: str
    source_chunk_id: str | None
    curriculum_mapping_id: str | None
    source_hash: str | None
    source_role: str
    source_metadata: dict[str, Any]


class ContentArtifactProvenanceResponse(BaseModel):
    artifact_id: uuid.UUID
    status: str
    artifact_hash: str
    source_snapshot_hash: str | None
    sources: list[ContentArtifactProvenanceSourceResponse]


class ContentArtifactReviewRequest(BaseModel):
    review_action: ContentReviewAction
    review_reason: str | None = None
    quality_score: float | None = Field(default=None, ge=0, le=1)


class ContentArtifactReviewResponse(BaseModel):
    review_id: uuid.UUID
    artifact_id: uuid.UUID
    review_action: str
    reviewer_id: str | None

class ContentGenerationRunCreateRequest(BaseModel):
    scope_id: str
    layers: list[ContentLayer] = Field(default_factory=lambda: [ContentLayer.DIAGNOSTIC_ITEMS, ContentLayer.LESSONS])
    dry_run: bool = True
    budget_cap: float | None = Field(default=None, ge=0)
    max_concurrency: int = Field(default=1, ge=1, le=20)


class ContentGenerationRunResponse(BaseModel):
    run_id: uuid.UUID
    scope_id: str
    status: str
    requested_by: str | None = None
    run_metadata: dict[str, Any] = Field(default_factory=dict)


class ContentGenerationTaskResponse(BaseModel):
    task_id: uuid.UUID
    run_id: uuid.UUID
    scope_id: str
    caps_ref: str | None
    content_layer: str
    status: str
    attempt_number: int = 1
    max_attempts: int = 3
    output_artifact_ids: list[str] = Field(default_factory=list)
    validation_failures: list[str] = Field(default_factory=list)


class ContentFactoryActionRequest(BaseModel):
    reason: str | None = None
    notes: str | None = None


class ContentFactoryActionResponse(BaseModel):
    artifact_id: uuid.UUID | None = None
    previous_status: str | None = None
    new_status: str | None = None
    status: str | None = None
    errors: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)


class ContentSeedRunResponse(BaseModel):
    seed_run_id: uuid.UUID
    scope_id: str
    dry_run: bool
    status: str
    summary: dict[str, Any] = Field(default_factory=dict)


class ContentFactoryReportResponse(BaseModel):
    scope_id: str
    generation_enabled: bool
    coverage: dict[str, Any]
    run_count: int
    review_queue_count: int


class ContentStagingVerificationRunResponse(BaseModel):
    run_id: uuid.UUID
    status: str
    summary: dict[str, Any] = Field(default_factory=dict)
    created_by: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
