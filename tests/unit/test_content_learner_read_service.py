"""Unit tests for learner production read service."""
from __future__ import annotations

import uuid

import pytest

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentProductionArtifact,
)
from app.services.content_learner_read_service import (
    ContentLearnerReadService,
    LearnerReadMode,
)


def test_learner_read_service_can_be_instantiated() -> None:
    """Learner read service can be instantiated."""
    service = ContentLearnerReadService()
    assert service is not None


def test_learner_read_service_has_get_diagnostic_items_method() -> None:
    """Learner read service has get_diagnostic_items method."""
    service = ContentLearnerReadService()
    assert hasattr(service, "get_diagnostic_items")


def test_learner_read_service_has_get_lessons_method() -> None:
    """Learner read service has get_lessons method."""
    service = ContentLearnerReadService()
    assert hasattr(service, "get_lessons")


def test_learner_read_service_has_get_scope_content_summary_method() -> None:
    """Learner read service has get_scope_content_summary method."""
    service = ContentLearnerReadService()
    assert hasattr(service, "get_scope_content_summary")


def test_learner_read_mode_enum_exists() -> None:
    """LearnerReadMode enum exists."""
    assert hasattr(LearnerReadMode, "PRODUCTION_ONLY")
    assert hasattr(LearnerReadMode, "PRODUCTION_WITH_LEGACY_FALLBACK")
    assert hasattr(LearnerReadMode, "LEGACY_ONLY")


def test_is_learner_visible_artifact_with_active_production() -> None:
    """Production active artifact is learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        provenance_valid=True,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is True


def test_is_learner_visible_artifact_without_production() -> None:
    """Artifact without production artifact is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        provenance_valid=True,
    )

    assert service.is_learner_visible_artifact(generation_artifact, None) is False


def test_is_learner_visible_artifact_with_inactive_production() -> None:
    """Artifact with inactive production status is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        provenance_valid=True,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="inactive",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is False


def test_is_learner_visible_artifact_with_pending_review() -> None:
    """Pending review artifact is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.PENDING_REVIEW,
        provenance_valid=True,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is False


def test_is_learner_visible_artifact_with_rejected() -> None:
    """Rejected artifact is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.REJECTED,
        provenance_valid=True,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is False


def test_is_learner_visible_artifact_with_quarantined() -> None:
    """Quarantined artifact is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.QUARANTINED,
        provenance_valid=True,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is False


def test_is_learner_visible_artifact_with_validation_failed() -> None:
    """Validation failed artifact is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.VALIDATION_FAILED,
        provenance_valid=True,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is False


def test_is_learner_visible_artifact_with_invalid_provenance() -> None:
    """Artifact with invalid provenance is not learner-visible."""
    service = ContentLearnerReadService()

    generation_artifact = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="test_scope",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        provenance_valid=False,
    )

    production_artifact = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=generation_artifact.artifact_id,
        scope_id="test_scope",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={},
        source_artifact_hash="test_hash",
        production_status="active",
    )

    assert service.is_learner_visible_artifact(generation_artifact, production_artifact) is False
