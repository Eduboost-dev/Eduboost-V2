"""Admin routes for the ETL-backed Content Factory."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.core.security import require_admin
from app.domain.content_factory_schemas import (
    ContentArtifactCreate,
    ContentArtifactResponse,
    ContentArtifactReviewRequest,
    ContentArtifactReviewResponse,
    ContentValidationReportResponse,
    SourceBundleValidationRequest,
    SourceBundleValidationResponse,
)
from app.services.content_factory import ContentFactoryService, ETLProvenanceService

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/content-factory",
    tags=["content_factory"],
    dependencies=[Depends(require_admin)],
)


@router.post("/source-bundles/validate", response_model=SourceBundleValidationResponse)
async def validate_source_bundle(request: SourceBundleValidationRequest) -> SourceBundleValidationResponse:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref=request.caps_ref,
        sources=[source.model_dump() for source in request.sources],
        min_sources=request.min_sources,
        require_approved_documents=request.require_approved_documents,
        allow_synthetic_without_source=request.allow_synthetic_without_source,
    )
    return SourceBundleValidationResponse(
        passed=result.passed,
        errors=result.errors,
        source_snapshot_hash=result.source_snapshot_hash,
    )


@router.post("/artifacts", response_model=ContentArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    request: ContentArtifactCreate,
    session: AsyncSession = Depends(get_db),
) -> ContentArtifactResponse:
    try:
        artifact = await ContentFactoryService().create_artifact(
            session,
            payload=request.model_dump(mode="json"),
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _artifact_response(artifact)


@router.get("/artifacts/{artifact_id}", response_model=ContentArtifactResponse)
async def get_artifact(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ContentArtifactResponse:
    try:
        artifact = await ContentFactoryService().get_artifact(session, artifact_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _artifact_response(artifact)


@router.post("/artifacts/{artifact_id}/validate", response_model=ContentValidationReportResponse)
async def validate_artifact(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ContentValidationReportResponse:
    try:
        report = await ContentFactoryService().validate_existing_artifact(session, artifact_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ContentValidationReportResponse(
        validation_report_id=report.validation_report_id,
        artifact_id=report.artifact_id,
        passed=report.passed,
        checks=report.checks,
        errors=report.errors,
    )


@router.post("/artifacts/{artifact_id}/reviews", response_model=ContentArtifactReviewResponse)
async def review_artifact(
    artifact_id: uuid.UUID,
    request: ContentArtifactReviewRequest,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> ContentArtifactReviewResponse:
    try:
        review = await ContentFactoryService().review_artifact(
            session,
            artifact_id=artifact_id,
            reviewer_id=current_user.get("sub"),
            review_action=request.review_action,
            review_reason=request.review_reason,
            quality_score=request.quality_score,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ContentArtifactReviewResponse(
        review_id=review.review_id,
        artifact_id=review.artifact_id,
        review_action=_value(review.review_action),
        reviewer_id=review.reviewer_id,
    )


def _artifact_response(artifact) -> ContentArtifactResponse:
    return ContentArtifactResponse(
        artifact_id=artifact.artifact_id,
        scope_id=artifact.scope_id,
        content_layer=_value(artifact.content_layer),
        artifact_type=_value(artifact.artifact_type),
        caps_ref=artifact.caps_ref,
        status=_value(artifact.status),
        artifact_hash=artifact.artifact_hash,
        source_snapshot_hash=artifact.source_snapshot_hash,
    )


def _value(value) -> str:
    return value.value if hasattr(value, "value") else str(value)
