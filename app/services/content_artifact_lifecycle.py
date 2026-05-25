"""Centralized Content Factory artifact lifecycle transitions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.services.content_factory import ContentFactoryService


@dataclass(frozen=True)
class ArtifactStatusTransition:
    artifact_id: uuid.UUID
    previous_status: str
    new_status: str
    actor_id: str
    reason: str | None = None


class ContentArtifactLifecycleService:
    def __init__(self, factory_service: ContentFactoryService | None = None) -> None:
        self.factory_service = factory_service or ContentFactoryService()

    async def create_artifact(self, session: AsyncSession, *, payload: dict[str, Any]) -> ContentGenerationArtifact:
        return await self.factory_service.create_artifact(session, payload=payload)

    async def validate_for_review(self, session: AsyncSession, artifact_id: uuid.UUID):
        return await self.factory_service.validate_existing_artifact(session, artifact_id)

    async def submit_for_review(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous not in {ContentArtifactStatus.GENERATED.value, ContentArtifactStatus.VALIDATION_FAILED.value}:
            raise ValueError("Only generated or validation_failed artifacts can be submitted for review.")
        report = await self.validate_for_review(session, artifact_id)
        if not report.passed:
            artifact.status = ContentArtifactStatus.VALIDATION_FAILED
            raise ValueError("Artifact validation failed: " + "; ".join(report.errors))
        artifact.status = ContentArtifactStatus.PENDING_REVIEW
        await session.flush()
        return ArtifactStatusTransition(artifact.artifact_id, previous, ContentArtifactStatus.PENDING_REVIEW.value, actor_id)

    async def approve_artifact(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str, notes: str = "") -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous != ContentArtifactStatus.PENDING_REVIEW.value:
            raise ValueError("Only pending_review artifacts can be approved.")
        await self.factory_service.assert_artifact_has_approved_sources(session, artifact_id)
        artifact.status = ContentArtifactStatus.APPROVED
        await session.flush()
        return ArtifactStatusTransition(artifact.artifact_id, previous, ContentArtifactStatus.APPROVED.value, actor_id, notes or None)

    async def reject_artifact(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str, reason: str) -> ArtifactStatusTransition:
        if not reason:
            raise ValueError("Rejecting an artifact requires a reason.")
        return await self._set_status(session, artifact_id, actor_id, ContentArtifactStatus.REJECTED, reason)

    async def quarantine_artifact(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str, reason: str) -> ArtifactStatusTransition:
        if not reason:
            raise ValueError("Quarantining an artifact requires a reason.")
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        if _value(artifact.status) == ContentArtifactStatus.PROMOTED_PRODUCTION.value:
            raise ValueError("Promoted production artifacts must be retired rather than quarantined.")
        previous = _value(artifact.status)
        artifact.status = ContentArtifactStatus.QUARANTINED
        await session.flush()
        return ArtifactStatusTransition(artifact.artifact_id, previous, ContentArtifactStatus.QUARANTINED.value, actor_id, reason)

    async def retire_artifact(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str, reason: str) -> ArtifactStatusTransition:
        if not reason:
            raise ValueError("Retiring an artifact requires a reason.")
        return await self._set_status(session, artifact_id, actor_id, ContentArtifactStatus.RETIRED, reason)

    async def mark_seeded_staging(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous != ContentArtifactStatus.APPROVED.value:
            raise ValueError("Only approved artifacts can be seeded to staging.")
        artifact.status = ContentArtifactStatus.SEEDED_STAGING
        await session.flush()
        return ArtifactStatusTransition(artifact.artifact_id, previous, ContentArtifactStatus.SEEDED_STAGING.value, actor_id)

    async def mark_promoted_production(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous != ContentArtifactStatus.SEEDED_STAGING.value:
            raise ValueError("Only seeded_staging artifacts can be promoted to production.")
        artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION
        await session.flush()
        return ArtifactStatusTransition(artifact.artifact_id, previous, ContentArtifactStatus.PROMOTED_PRODUCTION.value, actor_id)

    async def _set_status(self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str, status: ContentArtifactStatus, reason: str | None) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous == ContentArtifactStatus.QUARANTINED.value and status == ContentArtifactStatus.APPROVED:
            raise ValueError("Quarantined artifacts require explicit revalidation before approval.")
        artifact.status = status
        await session.flush()
        return ArtifactStatusTransition(artifact.artifact_id, previous, status.value, actor_id, reason)


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
