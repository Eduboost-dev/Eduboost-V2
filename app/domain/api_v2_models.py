"""Shared Pydantic models for the EduBoost V2 API contract.

This module intentionally contains transport-layer models only. Domain entities,
database models, and service-internal DTOs should remain outside this file.

The generic API envelope models are introduced ahead of the route migration in
PR-002R. Existing endpoint-specific models are kept here to avoid breaking
current router imports while the response envelope is rolled out incrementally.
"""
from __future__ import annotations

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiMeta(BaseModel):
    """Metadata included with every V2 API response."""

    api_version: str = "v2"
    request_id: str | None = None
    pagination: "PaginationMeta | None" = None


class FieldError(BaseModel):
    """Machine-readable validation detail for a single request field."""

    field: str
    message: str
    code: str = "invalid"


class ApiError(BaseModel):
    """Canonical V2 error payload."""

    code: str
    message: str
    field_errors: list[FieldError] = Field(default_factory=list)
    remediation: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class PaginationMeta(BaseModel):
    """Pagination metadata for list endpoints."""

    limit: int = Field(ge=0)
    offset: int | None = Field(default=None, ge=0)
    cursor: str | None = None
    next_cursor: str | None = None
    total: int | None = Field(default=None, ge=0)
    has_more: bool = False


class ApiEnvelope(BaseModel, Generic[DataT]):
    """Canonical V2 response envelope.

    Success responses set ``data`` and leave ``error`` as ``None``.
    Error responses set ``error`` and leave ``data`` as ``None``.
    """

    data: DataT | None = None
    error: ApiError | None = None
    meta: ApiMeta = Field(default_factory=ApiMeta)


class ApiSuccessEnvelope(ApiEnvelope[DataT], Generic[DataT]):
    """Typed success envelope alias for OpenAPI readability."""

    error: None = None


class ApiErrorEnvelope(ApiEnvelope[None]):
    """Typed error envelope alias for OpenAPI readability."""

    data: None = None
    error: ApiError


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    version: str | None = None
    environment: str | None = None
    mode: str | None = None


class StudyPlanGenerateRequest(BaseModel):
    gap_ratio: float = Field(default=0.4, ge=0.0, le=1.0)


class JobAcceptedResponse(BaseModel):
    job_id: str
    operation: str
    status: str = "queued"


class JobStatusResponse(JobAcceptedResponse):
    payload: dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    error: dict[str, Any] | None = None
    created_at: str
    updated_at: str


class RLHFExportRequest(BaseModel):
    records: list[dict[str, Any]] = Field(default_factory=list)


ApiMeta.model_rebuild()
