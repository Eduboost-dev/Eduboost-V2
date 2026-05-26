"""Unit tests for production read verification service."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentProductionArtifact,
    ContentPromotionEvent,
)
from app.services.content_production_read_verification import (
    ContentProductionReadVerificationService,
)
from tests.conftest import async_test


@async_test
async def test_production_read_verification_fails_if_promoted_record_is_missing(session: AsyncSession) -> None:
    """Production read verification fails if promoted record is missing."""
    service = ContentProductionReadVerificationService()
    promotion_event_id = uuid.uuid4()
    
    report = await service.verify_promotion_event(session, promotion_event_id)
    
    assert not report.passed
    assert any("not found" in error for error in report.errors)


@async_test
async def test_production_read_verification_fails_if_production_record_points_to_non_approved_artifact(session: AsyncSession) -> None:
    """Production read verification fails if production record points to non-approved artifact."""
    service = ContentProductionReadVerificationService()
    promotion_event_id = uuid.uuid4()
    artifact_id = uuid.uuid4()
    
    # Create a promotion event
    promotion_event = ContentPromotionEvent(
        event_id=promotion_event_id,
        scope_id="test_scope",
        promoted_by="admin",
        status="succeeded",
        summary={},
    )
    session.add(promotion_event)
    await session.flush()
    
    # Create a non-approved artifact
    artifact = ContentGenerationArtifact(
        artifact_id=artifact_id,
        scope_id="test_scope",
        caps_ref="test_ref",
        layer="lessons",
        artifact_type="lesson",
        payload_json={},
        source_artifact_hash="test_hash",
        status=ContentArtifactStatus.PENDING_REVIEW,
        provenance_valid=True,
    )
    session.add(artifact)
    await session.flush()
    
    # Create a production artifact pointing to the non-approved artifact
    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=artifact_id,
        staging_artifact_id=None,
        scope_id="test_scope",
        caps_ref="test_ref",
        layer="lessons",
        artifact_type="lesson",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
        created_by_promotion_event_id=promotion_event_id,
    )
    session.add(production_artifact)
    await session.flush()
    
    report = await service.verify_promotion_event(session, promotion_event_id)
    
    assert not report.passed
    assert any("non-approved" in error for error in report.errors)


@async_test
async def test_production_read_verification_passes_for_valid_promoted_records(session: AsyncSession) -> None:
    """Production read verification passes for valid promoted records."""
    service = ContentProductionReadVerificationService()
    promotion_event_id = uuid.uuid4()
    artifact_id = uuid.uuid4()
    
    # Create a promotion event
    promotion_event = ContentPromotionEvent(
        event_id=promotion_event_id,
        scope_id="test_scope",
        promoted_by="admin",
        status="succeeded",
        summary={},
    )
    session.add(promotion_event)
    await session.flush()
    
    # Create an approved artifact
    artifact = ContentGenerationArtifact(
        artifact_id=artifact_id,
        scope_id="test_scope",
        caps_ref="test_ref",
        layer="lessons",
        artifact_type="lesson",
        payload_json={},
        source_artifact_hash="test_hash",
        status=ContentArtifactStatus.APPROVED,
        provenance_valid=True,
    )
    session.add(artifact)
    await session.flush()
    
    # Create a production artifact pointing to the approved artifact
    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=artifact_id,
        staging_artifact_id=None,
        scope_id="test_scope",
        caps_ref="test_ref",
        layer="lessons",
        artifact_type="lesson",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
        created_by_promotion_event_id=promotion_event_id,
    )
    session.add(production_artifact)
    await session.flush()
    
    report = await service.verify_promotion_event(session, promotion_event_id)
    
    assert report.passed
    assert report.verified_count == 1
