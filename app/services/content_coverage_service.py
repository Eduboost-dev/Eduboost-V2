"""Registry-backed Content Factory coverage calculations."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from app.domain.content_coverage import (
    CapsRefCoverageReport,
    ContentLayer,
    CoverageGap,
    CoverageGapReport,
    CoverageLayerCounts,
    CoverageLayerStatus,
    MultiScopeCoverageSummary,
    ScopeCoverageLayerSummary,
    ScopeCoverageReport,
    ScopeCoverageSummary,
    coverage_status,
)
from sqlalchemy import func, select

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.lesson_repository import LessonRepository
from app.services.content_scope_registry import ContentScopeRegistry


@dataclass(frozen=True)
class CoverageGateLayerReport:
    status: CoverageLayerStatus
    coverage_percentage: float
    target_percentage: float
    approved_total: int
    target_total: int


DEFAULT_COVERAGE_LAYERS = [
    ContentLayer.DIAGNOSTIC_ITEMS,
    ContentLayer.LESSONS,
    ContentLayer.ASSESSMENT_BLUEPRINTS,
    ContentLayer.STUDY_PLAN_TEMPLATES,
]


class DiagnosticCoverageRepository(Protocol):
    async def get_coverage_summary(self, caps_refs: list[str] | None = None) -> dict[str, dict[str, Any]]:
        ...


class LessonCoverageRepository(Protocol):
    async def list_by_caps_ref(self, caps_ref: str, include_all_statuses: bool = False) -> Sequence[Any]:
        ...


class ContentCoverageService:
    def __init__(
        self,
        *,
        scope_registry: ContentScopeRegistry | None = None,
        item_repo: DiagnosticCoverageRepository | None = None,
        lesson_repo: LessonCoverageRepository | None = None,
    ) -> None:
        self.scope_registry = scope_registry or ContentScopeRegistry()
        self.item_repo = item_repo
        self.lesson_repo = lesson_repo

    async def get_scope_coverage(
        self,
        scope_id: str,
        layers: list[ContentLayer] | None = None,
    ) -> ScopeCoverageReport:
        scope = self.scope_registry.get_scope(scope_id)
        selected_layers = layers or DEFAULT_COVERAGE_LAYERS
        per_caps_ref = [
            await self.get_caps_ref_coverage(scope_id, caps_ref, layers=selected_layers)
            for caps_ref in scope.caps_refs
        ]
        return ScopeCoverageReport(
            scope_id=scope.scope_id,
            grade=scope.grade,
            subject_code=scope.subject_code,
            language=scope.language,
            summary=self._summarize_caps_refs(per_caps_ref),
            layers=self._summarize_layers(per_caps_ref, selected_layers),
            per_caps_ref=per_caps_ref,
        )

    async def get_coverage_by_grade(
        self,
        grade: int,
        layers: list[ContentLayer] | None = None,
    ) -> list[ScopeCoverageReport]:
        """Get coverage reports for all scopes at a specific grade."""
        reports = []
        for scope in self.scope_registry.list_scopes():
            if scope.grade == grade:
                reports.append(await self.get_scope_coverage(scope.scope_id, layers))
        return reports

    async def get_coverage_by_subject(
        self,
        subject_code: str,
        layers: list[ContentLayer] | None = None,
    ) -> list[ScopeCoverageReport]:
        """Get coverage reports for all scopes of a specific subject."""
        reports = []
        for scope in self.scope_registry.list_scopes():
            if scope.subject_code == subject_code:
                reports.append(await self.get_scope_coverage(scope.scope_id, layers))
        return reports

    async def get_coverage_summary_all_scopes(
        self,
        layers: list[ContentLayer] | None = None,
    ) -> MultiScopeCoverageSummary:
        """Get an aggregate coverage summary across all scopes."""
        reports = []
        scopes_by_status: dict[str, int] = {}
        scopes_by_grade: dict[str, int] = {}
        scopes_by_subject: dict[str, int] = {}

        for scope in self.scope_registry.list_scopes():
            status = scope.status.value
            scopes_by_status[status] = scopes_by_status.get(status, 0) + 1
            
            grade_key = str(scope.grade) if scope.grade is not None else "R"
            scopes_by_grade[grade_key] = scopes_by_grade.get(grade_key, 0) + 1
            
            subj = scope.subject_code or "unknown"
            scopes_by_subject[subj] = scopes_by_subject.get(subj, 0) + 1
            
            reports.append(await self.get_scope_coverage(scope.scope_id, layers))

        selected_layers = layers or DEFAULT_COVERAGE_LAYERS
        
        green = amber = red = not_configured = 0
        total_caps_refs = 0
        for report in reports:
            total_caps_refs += report.summary.total_caps_refs
            green += report.summary.green_refs
            amber += report.summary.amber_refs
            red += report.summary.red_refs
            not_configured += report.summary.not_configured_refs
            
        global_summary = ScopeCoverageSummary(
            total_caps_refs=total_caps_refs,
            green_refs=green,
            amber_refs=amber,
            red_refs=red,
            not_configured_refs=not_configured,
        )

        global_layers: dict[ContentLayer, ScopeCoverageLayerSummary] = {}
        for layer in selected_layers:
            target_total = sum(report.layers[layer].target_total for report in reports)
            approved_total = sum(report.layers[layer].approved_total for report in reports)
            global_layers[layer] = ScopeCoverageLayerSummary(
                target_total=target_total,
                approved_total=approved_total,
                coverage_ratio=round(approved_total / target_total, 4) if target_total else 0.0,
            )

        return MultiScopeCoverageSummary(
            total_scopes=len(reports),
            scopes_by_status=scopes_by_status,
            scopes_by_grade=scopes_by_grade,
            scopes_by_subject=scopes_by_subject,
            global_summary=global_summary,
            global_layers=global_layers,
        )

    async def get_coverage_gap_report(
        self,
        grade: int | None = None,
        subject_code: str | None = None,
        layers: list[ContentLayer] | None = None,
    ) -> CoverageGapReport:
        """Get a report of all CAPS references that are below target."""
        reports = []
        for scope in self.scope_registry.list_scopes():
            if grade is not None and scope.grade != grade:
                continue
            if subject_code is not None and scope.subject_code != subject_code:
                continue
            reports.append(await self.get_scope_coverage(scope.scope_id, layers))
            
        gaps = []
        selected_layers = layers or DEFAULT_COVERAGE_LAYERS
        
        for report in reports:
            for caps_report in report.per_caps_ref:
                for layer in selected_layers:
                    counts = caps_report.layers[layer]
                    if counts.target > 0 and counts.approved < counts.target:
                        gaps.append(
                            CoverageGap(
                                scope_id=report.scope_id,
                                caps_ref=caps_report.caps_ref,
                                layer=layer,
                                target=counts.target,
                                approved=counts.approved,
                                gap=counts.target - counts.approved,
                            )
                        )
                        
        return CoverageGapReport(gaps=gaps, total_gaps=len(gaps))

    async def get_coverage(
        self,
        session: Any,
        scope_id: str,
        layer: ContentLayer,
    ) -> CoverageGateLayerReport:
        """Return layer-level coverage in the shape expected by promotion gates.

        The session parameter is accepted for compatibility with DB-backed gate
        callers; this service already receives its repositories at construction.
        """
        layer = ContentLayer(layer)
        scope_report = await self.get_scope_coverage(scope_id, layers=[layer])
        layer_summary = scope_report.layers[layer]
        approved_total = layer_summary.approved_total

        if layer in {ContentLayer.ASSESSMENT_BLUEPRINTS, ContentLayer.STUDY_PLAN_TEMPLATES}:
            approved_total = await self._artifact_layer_approved_total(session, scope_id, layer)

        status = coverage_status(approved_total, layer_summary.target_total)
        coverage_ratio = round(approved_total / layer_summary.target_total, 4) if layer_summary.target_total else 0.0
        return CoverageGateLayerReport(
            status=status,
            coverage_percentage=round(coverage_ratio * 100, 2),
            target_percentage=100.0,
            approved_total=approved_total,
            target_total=layer_summary.target_total,
        )

    async def get_caps_ref_coverage(
        self,
        scope_id: str,
        caps_ref: str,
        layers: list[ContentLayer] | None = None,
    ) -> CapsRefCoverageReport:
        if caps_ref not in self.scope_registry.get_scope_caps_refs(scope_id):
            raise LookupError(f"CAPS reference {caps_ref} is outside content scope {scope_id}.")

        selected_layers = layers or DEFAULT_COVERAGE_LAYERS
        return CapsRefCoverageReport(
            scope_id=scope_id,
            caps_ref=caps_ref,
            layers={
                layer: await self._layer_counts(scope_id, caps_ref, layer)
                for layer in selected_layers
            },
        )

    async def _layer_counts(self, scope_id: str, caps_ref: str, layer: ContentLayer) -> CoverageLayerCounts:
        try:
            target = self.scope_registry.get_coverage_target(scope_id, caps_ref, layer)
        except LookupError:
            target = 0

        if layer == ContentLayer.DIAGNOSTIC_ITEMS:
            counts = await self._diagnostic_counts(caps_ref)
        elif layer == ContentLayer.LESSONS:
            counts = await self._lesson_counts(caps_ref)
        else:
            counts = {"approved": 0, "pending_review": 0, "rejected": 0, "generated": 0}

        approved = counts["approved"]
        return CoverageLayerCounts(
            target=target,
            approved=approved,
            pending_review=counts["pending_review"],
            rejected=counts["rejected"],
            generated=counts["generated"],
            status=coverage_status(approved, target),
            coverage_ratio=round(approved / target, 4) if target > 0 else 0.0,
        )


    async def _artifact_layer_approved_total(self, session: Any, scope_id: str, layer: ContentLayer) -> int:
        if session is None or not hasattr(session, "execute"):
            return 0
        result = await session.execute(
            select(func.count(ContentGenerationArtifact.artifact_id)).where(
                ContentGenerationArtifact.scope_id == scope_id,
                ContentGenerationArtifact.content_layer == layer,
                ContentGenerationArtifact.status == ContentArtifactStatus.APPROVED,
            )
        )
        scalar = result.scalar_one_or_none() if hasattr(result, "scalar_one_or_none") else result.scalar()
        return int(scalar or 0)

    async def _diagnostic_counts(self, caps_ref: str) -> dict[str, int]:
        if self.item_repo is None:
            return {"approved": 0, "pending_review": 0, "rejected": 0, "generated": 0}

        summary = await self.item_repo.get_coverage_summary([caps_ref])
        counts = summary.get(caps_ref, {})
        return {
            "approved": int(counts.get("approved", 0)),
            "pending_review": int(counts.get("ai_generated", 0)) + int(counts.get("human_reviewed", 0)),
            "rejected": int(counts.get("rejected", 0)),
            "generated": int(counts.get("ai_generated", 0)),
        }

    async def _lesson_counts(self, caps_ref: str) -> dict[str, int]:
        if self.lesson_repo is None:
            return {"approved": 0, "pending_review": 0, "rejected": 0, "generated": 0}

        lessons = await self.lesson_repo.list_by_caps_ref(caps_ref, include_all_statuses=True)
        return {
            "approved": sum(1 for lesson in lessons if _status(lesson) == "approved"),
            "pending_review": sum(1 for lesson in lessons if _status(lesson) in {"ai_generated", "human_reviewed"}),
            "rejected": sum(1 for lesson in lessons if _status(lesson) == "rejected"),
            "generated": sum(1 for lesson in lessons if _status(lesson) == "ai_generated"),
        }

    def _summarize_caps_refs(self, per_caps_ref: list[CapsRefCoverageReport]) -> ScopeCoverageSummary:
        green = amber = red = not_configured = 0
        for report in per_caps_ref:
            statuses = {layer.status.value for layer in report.layers.values()}
            if "red" in statuses:
                red += 1
            elif "amber" in statuses:
                amber += 1
            elif statuses and statuses <= {"not_configured"}:
                not_configured += 1
            else:
                green += 1

        return ScopeCoverageSummary(
            total_caps_refs=len(per_caps_ref),
            green_refs=green,
            amber_refs=amber,
            red_refs=red,
            not_configured_refs=not_configured,
        )

    def _summarize_layers(
        self,
        per_caps_ref: list[CapsRefCoverageReport],
        layers: list[ContentLayer],
    ) -> dict[ContentLayer, ScopeCoverageLayerSummary]:
        summaries: dict[ContentLayer, ScopeCoverageLayerSummary] = {}
        for layer in layers:
            target_total = sum(report.layers[layer].target for report in per_caps_ref)
            approved_total = sum(report.layers[layer].approved for report in per_caps_ref)
            summaries[layer] = ScopeCoverageLayerSummary(
                target_total=target_total,
                approved_total=approved_total,
                coverage_ratio=round(approved_total / target_total, 4) if target_total else 0.0,
            )
        return summaries


def build_content_coverage_service(
    item_repo: ItemBankRepository,
    lesson_repo: LessonRepository,
) -> ContentCoverageService:
    return ContentCoverageService(item_repo=item_repo, lesson_repo=lesson_repo)


def _status(entity: Any) -> str:
    value = getattr(entity, "review_status", "")
    return value.value if hasattr(value, "value") else str(value)
