"""Staging seed and production promotion gates for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact, ContentSeedRun
from app.services.content_coverage_service import ContentCoverageService
from app.services.content_factory import ContentFactoryService

REQUIRED_PROMOTION_LAYERS = [ContentLayer.DIAGNOSTIC_ITEMS, ContentLayer.LESSONS]


@dataclass(frozen=True)
class GateResult:
    passed: bool
    errors: list[str]
    summary: dict[str, Any]


class ContentSeedPromotionService:
    def __init__(self, coverage_service: ContentCoverageService, factory_service: ContentFactoryService | None = None) -> None:
        self.coverage_service = coverage_service
        self.factory_service = factory_service or ContentFactoryService()

    async def dry_run_seed(self, session: AsyncSession, scope_id: str, layer: ContentLayer | None = None) -> ContentSeedRun:
        gate = await self._seed_gate(session, scope_id, layer)
        run = ContentSeedRun(seed_run_id=uuid.uuid4(), scope_id=scope_id, dry_run=True, status="passed" if gate.passed else "blocked", summary={"errors": gate.errors, **gate.summary})
        session.add(run)
        await session.flush()
        return run

    async def seed_staging(self, session: AsyncSession, scope_id: str, actor_id: str, allow_partial: bool = True) -> ContentSeedRun:
        gate = await self._seed_gate(session, scope_id, None)
        stageable_count = int(gate.summary.get("stageable_approved", 0))
        if not gate.passed and (not allow_partial or stageable_count <= 0):
            raise ValueError("Staging seed gate failed: " + "; ".join(gate.errors))
        run_status = "seeded_staging" if gate.passed else "partially_seeded_staging"
        run = ContentSeedRun(seed_run_id=uuid.uuid4(), scope_id=scope_id, dry_run=False, status=run_status, summary={"actor_id": actor_id, "allow_partial": allow_partial, "errors": gate.errors, **gate.summary})
        session.add(run)
        await session.flush()
        return run

    async def verify_staging_seed(self, session: AsyncSession, scope_id: str) -> GateResult:
        return await self._seed_gate(session, scope_id, None)

    async def promote_production(self, session: AsyncSession, scope_id: str, actor_id: str) -> GateResult:
        gate = await self._seed_gate(session, scope_id, None)
        if not gate.passed:
            raise ValueError("Production promotion gate failed: " + "; ".join(gate.errors))
        return GateResult(True, [], {"scope_id": scope_id, "actor_id": actor_id, "status": "promotion_allowed"})

    async def rollback_staging_seed(self, session: AsyncSession, seed_run_id: str, actor_id: str) -> GateResult:
        run = await session.get(ContentSeedRun, uuid.UUID(str(seed_run_id)))
        if run is None:
            raise LookupError(f"Seed run {seed_run_id} not found.")
        run.status = "rolled_back"
        summary = dict(run.summary or {})
        summary["rollback_actor_id"] = actor_id
        run.summary = summary
        await session.flush()
        return GateResult(True, [], {"seed_run_id": seed_run_id, "status": "rolled_back"})

    async def _seed_gate(self, session: AsyncSession, scope_id: str, layer: ContentLayer | None) -> GateResult:
        layers = [layer] if layer else REQUIRED_PROMOTION_LAYERS
        coverage = await self.coverage_service.get_scope_coverage(scope_id, layers=layers)
        errors: list[str] = []
        stageable_approved = 0
        for caps_ref in coverage.per_caps_ref:
            for content_layer, counts in caps_ref.layers.items():
                stageable_approved += int(counts.approved or 0)
                if counts.status != CoverageLayerStatus.GREEN:
                    errors.append(f"{caps_ref.caps_ref}:{content_layer.value} coverage is {counts.status.value}.")

        result = await session.execute(select(ContentGenerationArtifact).where(ContentGenerationArtifact.scope_id == scope_id))
        artifacts = list(result.scalars().all())
        for artifact in artifacts:
            status = _value(artifact.status)
            if status in {ContentArtifactStatus.REJECTED.value, ContentArtifactStatus.QUARANTINED.value, ContentArtifactStatus.VALIDATION_FAILED.value}:
                errors.append(f"Artifact {artifact.artifact_id} has blocking status {status}.")

        blocking_artifact_count = sum(1 for artifact in artifacts if _value(artifact.status) in {ContentArtifactStatus.REJECTED.value, ContentArtifactStatus.QUARANTINED.value, ContentArtifactStatus.VALIDATION_FAILED.value})
        return GateResult(not errors, errors, {"scope_id": scope_id, "layers": [item.value for item in layers], "stageable_approved": stageable_approved, "blocking_artifact_count": blocking_artifact_count})


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
