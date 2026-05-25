import pytest

from app.domain.content_coverage import ContentLayer, CoverageLayerCounts, CoverageLayerStatus, ScopeCoverageLayerSummary, ScopeCoverageReport, ScopeCoverageSummary, CapsRefCoverageReport
from app.services.content_seed_promotion import ContentSeedPromotionService


class FakeCoverageService:
    def __init__(self, status: CoverageLayerStatus) -> None:
        self.status = status

    async def get_scope_coverage(self, scope_id, layers=None):
        selected = layers or [ContentLayer.DIAGNOSTIC_ITEMS]
        return ScopeCoverageReport(
            scope_id=scope_id,
            grade=4,
            subject_code="MAT",
            language="en",
            summary=ScopeCoverageSummary(total_caps_refs=1, green_refs=1 if self.status == CoverageLayerStatus.GREEN else 0, amber_refs=1 if self.status == CoverageLayerStatus.AMBER else 0, red_refs=1 if self.status == CoverageLayerStatus.RED else 0, not_configured_refs=0),
            layers={layer: ScopeCoverageLayerSummary(target_total=1, approved_total=1 if self.status == CoverageLayerStatus.GREEN else 0, coverage_ratio=1.0 if self.status == CoverageLayerStatus.GREEN else 0.0) for layer in selected},
            per_caps_ref=[CapsRefCoverageReport(scope_id=scope_id, caps_ref="4.M.1.1", layers={layer: CoverageLayerCounts(target=1, approved=1 if self.status == CoverageLayerStatus.GREEN else 0, status=self.status) for layer in selected})],
        )


class Result:
    def scalars(self):
        return self
    def all(self):
        return []


class Session:
    def add(self, obj):
        self.obj = obj
    async def flush(self):
        return None
    async def execute(self, stmt):
        return Result()


@pytest.mark.asyncio
async def test_seed_gate_fails_when_coverage_is_red() -> None:
    service = ContentSeedPromotionService(FakeCoverageService(CoverageLayerStatus.RED))
    with pytest.raises(ValueError):
        await service.seed_staging(Session(), "grade4_mathematics_en", "admin")


@pytest.mark.asyncio
async def test_dry_run_seed_records_blocked_result() -> None:
    service = ContentSeedPromotionService(FakeCoverageService(CoverageLayerStatus.RED))
    run = await service.dry_run_seed(Session(), "grade4_mathematics_en")
    assert run.status == "blocked"
