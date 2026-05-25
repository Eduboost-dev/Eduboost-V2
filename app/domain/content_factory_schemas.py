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


class ContentArtifactReviewRequest(BaseModel):
    review_action: ContentReviewAction
    review_reason: str | None = None
    quality_score: float | None = Field(default=None, ge=0, le=1)


class ContentArtifactReviewResponse(BaseModel):
    review_id: uuid.UUID
    artifact_id: uuid.UUID
    review_action: str
    reviewer_id: str | None
