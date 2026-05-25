"""Admin routes for the ETL-backed Content Factory."""
from __future__ import annotations

import sys
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.core.security import require_admin
from app.domain.content_factory_schemas import (
    ContentArtifactProvenanceResponse,
    ContentArtifactProvenanceSourceResponse,
    ContentArtifactValidationRequest,
    ContentArtifactValidationResponse,
    ContentFactoryETLStatusResponse,
    ContentFactoryHealthResponse,
)
from app.services.content_factory import ContentFactoryService, ContentValidationService

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/content-factory",
    tags=["admin-content-factory"],
    dependencies=[Depends(require_admin)],
)


@router.get("/health", response_model=ContentFactoryHealthResponse)
async def content_factory_health() -> ContentFactoryHealthResponse:
    return ContentFactoryHealthResponse(
        status="ok",
        route_scope="admin",
        generation_enabled=False,
    )


@router.get("/etl/status", response_model=ContentFactoryETLStatusResponse)
async def etl_status() -> ContentFactoryETLStatusResponse:
    return ContentFactoryETLStatusResponse(
        status="available",
        pipeline_package="app.services.etl",
        mcp_runtime_imported=_mcp_runtime_imported(),
        notes=[
            "ETL pipeline modules are importable from app.services.etl.",
            "MCP server wrappers are isolated under tools/etl and are not imported by app startup.",
        ],
    )


@router.post("/validate-artifact", response_model=ContentArtifactValidationResponse)
async def validate_artifact_payload(
    request: ContentArtifactValidationRequest,
) -> ContentArtifactValidationResponse:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json=request.artifact_json,
        caps_ref=request.caps_ref,
        sources=[source.model_dump() for source in request.sources],
        artifact_type=request.artifact_type.value,
        min_sources=request.min_sources,
    )
    return ContentArtifactValidationResponse(
        passed=result["passed"],
        checks=result["checks"],
        errors=result["errors"],
        source_snapshot_hash=result["source_snapshot_hash"],
    )


@router.get("/provenance/{artifact_id}", response_model=ContentArtifactProvenanceResponse)
async def get_artifact_provenance(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ContentArtifactProvenanceResponse:
    try:
        artifact = await ContentFactoryService().get_artifact(session, artifact_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ContentArtifactProvenanceResponse(
        artifact_id=artifact.artifact_id,
        status=_value(artifact.status),
        artifact_hash=artifact.artifact_hash,
        source_snapshot_hash=artifact.source_snapshot_hash,
        sources=[
            ContentArtifactProvenanceSourceResponse(
                source_document_id=source.source_document_id,
                source_chunk_id=source.source_chunk_id,
                curriculum_mapping_id=source.curriculum_mapping_id,
                source_hash=source.source_hash,
                source_role=source.source_role,
                source_metadata=source.source_metadata or {},
            )
            for source in artifact.sources
        ],
    )


def _mcp_runtime_imported() -> bool:
    return any(name.startswith("mcp.") or name == "mcp" for name in sys.modules)


def _value(value) -> str:
    return value.value if hasattr(value, "value") else str(value)
