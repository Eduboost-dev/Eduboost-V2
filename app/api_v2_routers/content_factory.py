"""Admin routes for the ETL-backed Content Factory."""
from __future__ import annotations

import os
import sys
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.core.security import get_current_user, require_admin
from app.domain.content_factory_schemas import (
    ContentArtifactProvenanceResponse,
    ContentArtifactProvenanceSourceResponse,
    ContentArtifactResponse,
    ContentArtifactValidationRequest,
    ContentArtifactValidationResponse,
    ContentFactoryActionRequest,
    ContentFactoryActionResponse,
    ContentFactoryETLStatusResponse,
    ContentFactoryHealthResponse,
    ContentFactoryReportResponse,
    ContentGenerationExecutionReportResponse,
    ContentGenerationExecutionResponse,
    ContentGenerationPlanResponse,
    ContentGenerationRunCreateRequest,
    ContentGenerationRunResponse,
    ContentGenerationTaskResponse,
    ContentSeedRunResponse,
    ContentStagingVerificationRunResponse,
)
from app.domain.content_coverage import CapsRefCoverageReport, ContentLayer, CoverageTarget, ScopeCoverageReport
from app.domain.content_scope import ContentScope
from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact, ContentGenerationTask
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.lesson_repository import LessonRepository
from app.services.content_artifact_lifecycle import ContentArtifactLifecycleService
from app.services.content_factory import ContentFactoryService, ContentValidationService
from app.services.content_factory_orchestrator import ContentFactoryOrchestrator
from app.services.content_generation_runs import ContentGenerationRunService
from app.services.content_generation_executor import ContentGenerationExecutor, GenerationDisabledError
from app.services.content_generation_planner import ContentGenerationPlanner
from app.services.content_coverage_service import ContentCoverageService
from app.services.content_scope_registry import ContentScopeRegistry
from app.services.content_seed_promotion import ContentSeedPromotionService
from app.services.content_staging_readiness import (
    AllScopeStagingVerificationReport,
    ContentStagingReadinessService,
    ScopeStagingVerificationReport,
)

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/content-factory",
    tags=["admin-content-factory"],
    dependencies=[Depends(require_admin)],
)


def get_content_coverage_service(session: AsyncSession = Depends(get_db)) -> ContentCoverageService:
    return ContentCoverageService(item_repo=ItemBankRepository(session), lesson_repo=LessonRepository(session))


def get_content_generation_run_service() -> ContentGenerationRunService:
    return ContentGenerationRunService()


def get_content_factory_service() -> ContentFactoryService:
    return ContentFactoryService()


def get_content_artifact_lifecycle_service() -> ContentArtifactLifecycleService:
    return ContentArtifactLifecycleService()


def get_content_factory_orchestrator() -> ContentFactoryOrchestrator:
    return ContentFactoryOrchestrator()


def get_content_generation_planner() -> ContentGenerationPlanner:
    return ContentGenerationPlanner()


def get_content_generation_executor() -> ContentGenerationExecutor:
    return ContentGenerationExecutor()


def get_seed_promotion_service(
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> ContentSeedPromotionService:
    return ContentSeedPromotionService(coverage_service)


def get_staging_readiness_service() -> ContentStagingReadinessService:
    return ContentStagingReadinessService()


@router.get("/health", response_model=ContentFactoryHealthResponse)
async def content_factory_health() -> ContentFactoryHealthResponse:
    return ContentFactoryHealthResponse(
        status="ok",
        route_scope="admin",
        generation_enabled=_generation_enabled(),
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


@router.get("/scopes", response_model=list[ContentScope])
async def list_content_scopes() -> list[ContentScope]:
    return ContentScopeRegistry().list_scopes()


@router.get("/scopes/{scope_id}", response_model=ContentScope)
async def get_content_scope(scope_id: str) -> ContentScope:
    try:
        return ContentScopeRegistry().get_scope(scope_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/targets", response_model=list[CoverageTarget])
async def get_content_scope_targets(scope_id: str) -> list[CoverageTarget]:
    try:
        return ContentScopeRegistry().get_scope_targets(scope_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/coverage", response_model=ScopeCoverageReport)
async def get_content_scope_coverage(
    scope_id: str,
    layer: list[ContentLayer] | None = Query(default=None),
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> ScopeCoverageReport:
    try:
        return await coverage_service.get_scope_coverage(scope_id, layers=layer)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/coverage/{caps_ref}", response_model=CapsRefCoverageReport)
async def get_content_caps_ref_coverage(
    scope_id: str,
    caps_ref: str,
    layer: list[ContentLayer] | None = Query(default=None),
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> CapsRefCoverageReport:
    try:
        return await coverage_service.get_caps_ref_coverage(scope_id, caps_ref, layers=layer)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/validate-artifact", response_model=ContentArtifactValidationResponse)
async def validate_artifact_payload(request: ContentArtifactValidationRequest) -> ContentArtifactValidationResponse:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json=request.artifact_json,
        caps_ref=request.caps_ref,
        sources=[source.model_dump() for source in request.sources],
        artifact_type=request.artifact_type.value,
        min_sources=request.min_sources,
    )
    return ContentArtifactValidationResponse(**result)


@router.get("/runs", response_model=list[ContentGenerationRunResponse])
async def list_generation_runs(
    scope_id: str | None = None,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
) -> list[ContentGenerationRunResponse]:
    runs = await service.list_runs(session, scope_id=scope_id)
    return [_run_response(run) for run in runs]


@router.post("/runs", response_model=ContentGenerationRunResponse)
async def create_generation_run(
    request: ContentGenerationRunCreateRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ContentGenerationRunResponse:
    if not request.dry_run and not _generation_enabled():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Generation execution is disabled by CONTENT_FACTORY_GENERATION_ENABLED.")
    run = await service.create_run(
        session,
        scope_id=request.scope_id,
        layers=request.layers,
        requested_by=str(current_user.get("sub") or "admin"),
        dry_run=request.dry_run or not _generation_enabled(),
        budget_cap=request.budget_cap,
        max_concurrency=request.max_concurrency,
    )
    await service.create_tasks_for_run(session, run.run_id)
    await session.commit()
    return _run_response(run)


@router.get("/runs/{run_id}", response_model=ContentGenerationRunResponse)
async def get_generation_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
) -> ContentGenerationRunResponse:
    try:
        return _run_response(await service.get_run(session, run_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/runs/{run_id}/tasks", response_model=list[ContentGenerationTaskResponse])
async def get_generation_run_tasks(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
) -> list[ContentGenerationTaskResponse]:
    return [_task_response(task) for task in await service.get_run_tasks(session, run_id)]


@router.post("/runs/{run_id}/plan-missing", response_model=ContentGenerationPlanResponse)
async def plan_missing_generation_tasks(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    planner: ContentGenerationPlanner = Depends(get_content_generation_planner),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ContentGenerationPlanResponse:
    try:
        plan = await planner.plan_missing_for_run(session, run_id, actor_id=str(current_user.get("sub") or "admin"))
        await session.commit()
        return ContentGenerationPlanResponse(run_id=plan.run_id, created_task_ids=plan.created_task_ids, skipped=plan.skipped, missing=plan.missing)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/execute", response_model=ContentGenerationExecutionResponse)
async def execute_generation_run(
    run_id: uuid.UUID,
    max_tasks: int | None = Query(default=None, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    executor: ContentGenerationExecutor = Depends(get_content_generation_executor),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ContentGenerationExecutionResponse:
    try:
        result = await executor.execute_run(session, run_id, max_tasks=max_tasks, actor_id=str(current_user.get("sub") or "admin"))
        await session.commit()
        return ContentGenerationExecutionResponse(run_id=result.run_id, status=result.status, summary=result.summary)
    except GenerationDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "generation_disabled", "message": str(exc)}) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/execute", response_model=ContentGenerationExecutionResponse)
async def execute_generation_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    executor: ContentGenerationExecutor = Depends(get_content_generation_executor),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ContentGenerationExecutionResponse:
    try:
        result = await executor.execute_task(session, task_id, actor_id=str(current_user.get("sub") or "admin"))
        await session.commit()
        return ContentGenerationExecutionResponse(task_id=result.task_id, status=result.status, artifact_ids=result.artifact_ids, errors=result.errors, provider=result.provider, mode=result.mode)
    except GenerationDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "generation_disabled", "message": str(exc)}) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/tasks/{task_id}", response_model=ContentGenerationTaskResponse)
async def get_generation_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ContentGenerationTaskResponse:
    task = await session.get(ContentGenerationTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Generation task {task_id} not found.")
    return _task_response(task)


@router.get("/runs/{run_id}/execution-report", response_model=ContentGenerationExecutionReportResponse)
async def get_generation_execution_report(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    executor: ContentGenerationExecutor = Depends(get_content_generation_executor),
) -> ContentGenerationExecutionReportResponse:
    try:
        return ContentGenerationExecutionReportResponse(**await executor.execution_report(session, run_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/cancel", response_model=ContentGenerationRunResponse)
async def cancel_generation_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ContentGenerationRunResponse:
    try:
        run = await service.cancel_run(session, run_id, str(current_user.get("sub") or "admin"))
        await session.commit()
        return _run_response(run)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/retry-failed", response_model=list[ContentGenerationTaskResponse])
async def retry_failed_generation_tasks(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[ContentGenerationTaskResponse]:
    tasks = await service.retry_failed_tasks(session, run_id, str(current_user.get("sub") or "admin"))
    await session.commit()
    return [_task_response(task) for task in tasks]


@router.get("/artifacts", response_model=list[ContentArtifactResponse])
async def list_artifacts(
    scope_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_db),
) -> list[ContentArtifactResponse]:
    stmt = select(ContentGenerationArtifact).order_by(ContentGenerationArtifact.created_at.desc()).limit(100)
    if scope_id:
        stmt = stmt.where(ContentGenerationArtifact.scope_id == scope_id)
    if status_filter:
        stmt = stmt.where(ContentGenerationArtifact.status == status_filter)
    result = await session.execute(stmt)
    return [_artifact_response(artifact) for artifact in result.scalars().all()]


@router.get("/artifacts/{artifact_id}", response_model=ContentArtifactResponse)
async def get_artifact(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentFactoryService = Depends(get_content_factory_service),
) -> ContentArtifactResponse:
    try:
        return _artifact_response(await service.get_artifact(session, artifact_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/artifacts/{artifact_id}/provenance", response_model=ContentArtifactProvenanceResponse)
@router.get("/provenance/{artifact_id}", response_model=ContentArtifactProvenanceResponse)
async def get_artifact_provenance(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentFactoryService = Depends(get_content_factory_service),
) -> ContentArtifactProvenanceResponse:
    try:
        artifact = await service.get_artifact(session, artifact_id)
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


@router.post("/artifacts/{artifact_id}/submit-review", response_model=ContentFactoryActionResponse)
async def submit_artifact_for_review(artifact_id: uuid.UUID, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: dict[str, Any] = Depends(get_current_user)) -> ContentFactoryActionResponse:
    try:
        transition = await lifecycle.submit_for_review(session, artifact_id, str(current_user.get("sub") or "admin"))
        await session.commit()
        return ContentFactoryActionResponse(**transition.__dict__)
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/artifacts/{artifact_id}/approve", response_model=ContentFactoryActionResponse)
async def approve_artifact(artifact_id: uuid.UUID, request: ContentFactoryActionRequest, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: dict[str, Any] = Depends(get_current_user)) -> ContentFactoryActionResponse:
    try:
        transition = await lifecycle.approve_artifact(session, artifact_id, str(current_user.get("sub") or "admin"), request.notes or "")
        await session.commit()
        return ContentFactoryActionResponse(**transition.__dict__)
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/artifacts/{artifact_id}/reject", response_model=ContentFactoryActionResponse)
async def reject_artifact(artifact_id: uuid.UUID, request: ContentFactoryActionRequest, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: dict[str, Any] = Depends(get_current_user)) -> ContentFactoryActionResponse:
    transition = await lifecycle.reject_artifact(session, artifact_id, str(current_user.get("sub") or "admin"), request.reason or "Rejected by admin")
    await session.commit()
    return ContentFactoryActionResponse(**transition.__dict__)


@router.post("/artifacts/{artifact_id}/quarantine", response_model=ContentFactoryActionResponse)
async def quarantine_artifact(artifact_id: uuid.UUID, request: ContentFactoryActionRequest, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: dict[str, Any] = Depends(get_current_user)) -> ContentFactoryActionResponse:
    transition = await lifecycle.quarantine_artifact(session, artifact_id, str(current_user.get("sub") or "admin"), request.reason or "Quarantined by admin")
    await session.commit()
    return ContentFactoryActionResponse(**transition.__dict__)


@router.get("/review-queue", response_model=list[ContentArtifactResponse])
async def get_review_queue(session: AsyncSession = Depends(get_db)) -> list[ContentArtifactResponse]:
    result = await session.execute(select(ContentGenerationArtifact).where(ContentGenerationArtifact.status == ContentArtifactStatus.PENDING_REVIEW).order_by(ContentGenerationArtifact.created_at.asc()).limit(100))
    return [_artifact_response(artifact) for artifact in result.scalars().all()]


@router.post("/staging-verification/all-scopes", response_model=AllScopeStagingVerificationReport)
async def run_all_scope_staging_verification(
    include_partial: bool = Query(default=True),
    include_pending_review: bool = Query(default=True),
    include_blockers: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AllScopeStagingVerificationReport:
    report = await service.verify_all_scopes(
        session,
        include_partial=include_partial,
        actor_id=str(current_user.get("sub") or "admin"),
        persist=True,
    )
    await session.commit()
    if not include_blockers:
        report = report.model_copy(update={"scopes": [scope.model_copy(update={"blockers": []}) for scope in report.scopes]})
    return report


@router.get("/staging-verification/runs", response_model=list[ContentStagingVerificationRunResponse])
async def list_staging_verification_runs(
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
) -> list[ContentStagingVerificationRunResponse]:
    runs = await service.list_runs(session)
    return [_staging_verification_run_response(run) for run in runs]


@router.get("/staging-verification/runs/{run_id}", response_model=AllScopeStagingVerificationReport)
async def get_staging_verification_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
) -> AllScopeStagingVerificationReport:
    try:
        return await service.get_run_report(session, run_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/scopes/{scope_id}/staging-verification", response_model=ScopeStagingVerificationReport)
async def run_scope_staging_verification(
    scope_id: str,
    include_partial: bool = Query(default=True),
    include_pending_review: bool = Query(default=True),
    include_blockers: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ScopeStagingVerificationReport:
    report = await service.verify_scope(
        scope_id,
        session=session,
        include_partial=include_partial,
        actor_id=str(current_user.get("sub") or "admin"),
    )
    if report.status.value == "blocked_by_missing_scope":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown content scope: {scope_id}")
    if not include_blockers:
        report = report.model_copy(update={"blockers": []})
    return report


@router.get("/scopes/{scope_id}/staging-readiness", response_model=ScopeStagingVerificationReport)
async def get_scope_staging_readiness(
    scope_id: str,
    include_partial: bool = Query(default=True),
    include_pending_review: bool = Query(default=True),
    include_blockers: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
) -> ScopeStagingVerificationReport:
    report = await service.verify_scope(scope_id, session=session, include_partial=include_partial)
    if report.status.value == "blocked_by_missing_scope":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown content scope: {scope_id}")
    if not include_blockers:
        report = report.model_copy(update={"blockers": []})
    return report


@router.post("/scopes/{scope_id}/dry-run-seed", response_model=ContentSeedRunResponse)
async def dry_run_seed(scope_id: str, layer: ContentLayer | None = None, session: AsyncSession = Depends(get_db), service: ContentSeedPromotionService = Depends(get_seed_promotion_service)) -> ContentSeedRunResponse:
    run = await service.dry_run_seed(session, scope_id, layer)
    await session.commit()
    return _seed_run_response(run)


@router.post("/scopes/{scope_id}/seed-staging", response_model=ContentSeedRunResponse)
async def seed_staging(scope_id: str, session: AsyncSession = Depends(get_db), service: ContentSeedPromotionService = Depends(get_seed_promotion_service), current_user: dict[str, Any] = Depends(get_current_user)) -> ContentSeedRunResponse:
    try:
        run = await service.seed_staging(session, scope_id, str(current_user.get("sub") or "admin"))
        await session.commit()
        return _seed_run_response(run)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/staging-verification", response_model=ContentFactoryActionResponse)
async def verify_staging_seed(scope_id: str, session: AsyncSession = Depends(get_db), service: ContentSeedPromotionService = Depends(get_seed_promotion_service)) -> ContentFactoryActionResponse:
    result = await service.verify_staging_seed(session, scope_id)
    return ContentFactoryActionResponse(status="passed" if result.passed else "blocked", errors=result.errors, summary=result.summary)


@router.post("/scopes/{scope_id}/promote-production", response_model=ContentFactoryActionResponse)
async def promote_production(scope_id: str, session: AsyncSession = Depends(get_db), service: ContentSeedPromotionService = Depends(get_seed_promotion_service), current_user: dict[str, Any] = Depends(get_current_user)) -> ContentFactoryActionResponse:
    try:
        result = await service.promote_production(session, scope_id, str(current_user.get("sub") or "admin"))
        return ContentFactoryActionResponse(status="passed" if result.passed else "blocked", errors=result.errors, summary=result.summary)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/reports/{scope_id}", response_model=ContentFactoryReportResponse)
async def get_content_factory_report(scope_id: str, coverage_service: ContentCoverageService = Depends(get_content_coverage_service), session: AsyncSession = Depends(get_db)) -> ContentFactoryReportResponse:
    coverage = await coverage_service.get_scope_coverage(scope_id)
    run_count = len((await session.execute(select(ContentGenerationArtifact.artifact_id).where(ContentGenerationArtifact.scope_id == scope_id))).all())
    review_queue = len((await session.execute(select(ContentGenerationArtifact.artifact_id).where(ContentGenerationArtifact.scope_id == scope_id, ContentGenerationArtifact.status == ContentArtifactStatus.PENDING_REVIEW))).all())
    return ContentFactoryReportResponse(scope_id=scope_id, generation_enabled=_generation_enabled(), coverage=coverage.model_dump(mode="json"), run_count=run_count, review_queue_count=review_queue)


def _mcp_runtime_imported() -> bool:
    return any(name.startswith("mcp.") or name == "mcp" for name in sys.modules)


def _generation_enabled() -> bool:
    return os.environ.get("CONTENT_FACTORY_GENERATION_ENABLED", "false").lower() in {"1", "true", "yes"}


def _run_response(run) -> ContentGenerationRunResponse:
    return ContentGenerationRunResponse(run_id=run.run_id, scope_id=run.scope_id, status=run.status, requested_by=run.requested_by, run_metadata=run.run_metadata or {})


def _task_response(task) -> ContentGenerationTaskResponse:
    return ContentGenerationTaskResponse(task_id=task.task_id, run_id=task.run_id, scope_id=task.scope_id, caps_ref=task.caps_ref, content_layer=_value(task.content_layer), status=task.status, attempt_number=task.attempt_number, max_attempts=task.max_attempts, output_artifact_ids=task.output_artifact_ids or [], validation_failures=task.validation_failures or [])


def _artifact_response(artifact) -> ContentArtifactResponse:
    return ContentArtifactResponse(artifact_id=artifact.artifact_id, scope_id=artifact.scope_id, content_layer=_value(artifact.content_layer), artifact_type=_value(artifact.artifact_type), caps_ref=artifact.caps_ref, status=_value(artifact.status), artifact_hash=artifact.artifact_hash, source_snapshot_hash=artifact.source_snapshot_hash)


def _seed_run_response(run) -> ContentSeedRunResponse:
    return ContentSeedRunResponse(seed_run_id=run.seed_run_id, scope_id=run.scope_id, dry_run=run.dry_run, status=run.status, summary=run.summary or {})


def _staging_verification_run_response(run) -> ContentStagingVerificationRunResponse:
    return ContentStagingVerificationRunResponse(
        run_id=run.run_id,
        status=run.status,
        summary=run.summary_json or {},
        created_by=run.created_by,
        created_at=run.created_at.isoformat() if run.created_at else None,
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
    )


def _value(value) -> str:
    return value.value if hasattr(value, "value") else str(value)
