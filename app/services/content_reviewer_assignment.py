"""Reviewer assignment workflow for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentGenerationArtifact, ContentReviewAssignment

OPEN_STATUSES = {"assigned", "in_review"}
RESOLVED_STATUSES = {"approved", "rejected", "cancelled", "expired"}


@dataclass(frozen=True)
class ReviewerWorkload:
    reviewer_id: str
    assigned: int
    in_review: int
    overdue: int
    total_open: int


class ContentReviewerAssignmentService:
    async def assign_artifact(
        self,
        session: AsyncSession,
        artifact_id: str | uuid.UUID,
        reviewer_id: str,
        assigned_by: str,
        *,
        priority: str = "normal",
        due_by: datetime | None = None,
    ) -> ContentReviewAssignment:
        artifact = await session.get(ContentGenerationArtifact, uuid.UUID(str(artifact_id)))
        if artifact is None:
            raise LookupError(f"Artifact {artifact_id} not found.")
        existing = await self._open_assignment(session, artifact.artifact_id)
        if existing is not None:
            existing.assigned_to = reviewer_id
            existing.assigned_by = assigned_by
            existing.priority = priority
            existing.due_by = due_by
            await session.flush()
            return existing
        assignment = ContentReviewAssignment(
            artifact_id=artifact.artifact_id,
            assigned_to=reviewer_id,
            assigned_by=assigned_by,
            priority=priority,
            due_by=due_by,
            status="assigned",
        )
        session.add(assignment)
        await session.flush()
        return assignment

    async def assign_batch(
        self,
        session: AsyncSession,
        artifact_ids: list[str | uuid.UUID],
        reviewer_id: str,
        assigned_by: str,
        *,
        priority: str = "normal",
    ) -> list[ContentReviewAssignment]:
        assignments = []
        for artifact_id in artifact_ids:
            assignments.append(await self.assign_artifact(session, artifact_id, reviewer_id, assigned_by, priority=priority))
        return assignments

    async def unassign_artifact(self, session: AsyncSession, artifact_id: str | uuid.UUID, actor_id: str) -> ContentReviewAssignment:
        assignment = await self._open_assignment(session, uuid.UUID(str(artifact_id)))
        if assignment is None:
            raise LookupError(f"Open assignment for artifact {artifact_id} not found.")
        assignment.status = "cancelled"
        assignment.resolved_at = datetime.now(timezone.utc)
        await session.flush()
        return assignment

    async def get_reviewer_workload(self, session: AsyncSession, reviewer_id: str) -> ReviewerWorkload:
        result = await session.execute(select(ContentReviewAssignment).where(ContentReviewAssignment.assigned_to == reviewer_id, ContentReviewAssignment.status.in_(list(OPEN_STATUSES))))
        assignments = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        return ReviewerWorkload(
            reviewer_id=reviewer_id,
            assigned=sum(1 for item in assignments if item.status == "assigned"),
            in_review=sum(1 for item in assignments if item.status == "in_review"),
            overdue=sum(1 for item in assignments if item.due_by is not None and item.due_by < now),
            total_open=len(assignments),
        )

    async def list_assignments(self, session: AsyncSession, *, reviewer_id: str | None = None, status: str | None = None, limit: int = 100) -> list[ContentReviewAssignment]:
        stmt = select(ContentReviewAssignment).order_by(ContentReviewAssignment.created_at.desc()).limit(limit)
        if reviewer_id:
            stmt = stmt.where(ContentReviewAssignment.assigned_to == reviewer_id)
        if status:
            stmt = stmt.where(ContentReviewAssignment.status == status)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _open_assignment(self, session: AsyncSession, artifact_id: uuid.UUID) -> ContentReviewAssignment | None:
        result = await session.execute(select(ContentReviewAssignment).where(ContentReviewAssignment.artifact_id == artifact_id, ContentReviewAssignment.status.in_(list(OPEN_STATUSES))).limit(1))
        return result.scalar_one_or_none()
