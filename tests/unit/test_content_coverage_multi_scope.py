from unittest.mock import MagicMock
import pytest

from app.domain.content_coverage import ContentLayer
from app.domain.content_scope import ContentScope, ContentScopeStatus
from app.services.content_coverage_service import ContentCoverageService
from app.services.content_scope_registry import ContentScopeRegistry


@pytest.fixture
def mock_registry():
    registry = MagicMock(spec=ContentScopeRegistry)
    
    scope_g4_math = ContentScope(
        scope_id="grade4_mathematics_en",
        grade=4,
        subject_code="math",
        subject="Mathematics",
        language="en",
        curriculum="caps",
        status=ContentScopeStatus.ACTIVE,
        phase="intermediate",
        caps_refs=["math_1"],
    )
    
    scope_g5_math = ContentScope(
        scope_id="grade5_mathematics_en",
        grade=5,
        subject_code="math",
        subject="Mathematics",
        language="en",
        curriculum="caps",
        status=ContentScopeStatus.REVIEW,
        phase="intermediate",
        caps_refs=["math_2"],
    )
    
    scope_g4_sci = ContentScope(
        scope_id="grade4_science_en",
        grade=4,
        subject_code="sci",
        subject="Science",
        language="en",
        curriculum="caps",
        status=ContentScopeStatus.ACTIVE,
        phase="intermediate",
        caps_refs=["sci_1"],
    )
    
    registry.list_scopes.return_value = [scope_g4_math, scope_g5_math, scope_g4_sci]
    return registry


@pytest.fixture
def mock_coverage_service(mock_registry):
    service = ContentCoverageService(scope_registry=mock_registry)
    # Mock the individual scope report generator so we just test the aggregation logic
    async def mock_get_scope_coverage(scope_id, layers=None):
        from app.domain.content_coverage import ScopeCoverageReport, ScopeCoverageSummary, ScopeCoverageLayerSummary, CapsRefCoverageReport, CoverageLayerCounts, CoverageLayerStatus
        
        counts = CoverageLayerCounts(target=10, approved=5, status=CoverageLayerStatus.AMBER)
        return ScopeCoverageReport(
            scope_id=scope_id,
            grade=int(scope_id[5]),
            subject_code=scope_id.split("_")[1][:4], # approx
            language="en",
            summary=ScopeCoverageSummary(total_caps_refs=1, green_refs=0, amber_refs=1, red_refs=0, not_configured_refs=0),
            layers={ContentLayer.LESSONS: ScopeCoverageLayerSummary(target_total=10, approved_total=5, coverage_ratio=0.5)},
            per_caps_ref=[
                CapsRefCoverageReport(
                    scope_id=scope_id,
                    caps_ref=scope_id + "_ref1",
                    layers={ContentLayer.LESSONS: counts}
                )
            ]
        )
    service.get_scope_coverage = mock_get_scope_coverage
    return service


@pytest.mark.asyncio
async def test_get_coverage_by_grade(mock_coverage_service):
    reports = await mock_coverage_service.get_coverage_by_grade(4, [ContentLayer.LESSONS])
    assert len(reports) == 2
    assert {r.scope_id for r in reports} == {"grade4_mathematics_en", "grade4_science_en"}


@pytest.mark.asyncio
async def test_get_coverage_by_subject(mock_coverage_service):
    reports = await mock_coverage_service.get_coverage_by_subject("math", [ContentLayer.LESSONS])
    assert len(reports) == 2
    assert {r.scope_id for r in reports} == {"grade4_mathematics_en", "grade5_mathematics_en"}


@pytest.mark.asyncio
async def test_get_coverage_summary_all_scopes(mock_coverage_service):
    summary = await mock_coverage_service.get_coverage_summary_all_scopes([ContentLayer.LESSONS])
    assert summary.total_scopes == 3
    assert summary.scopes_by_status["active"] == 2
    assert summary.scopes_by_status["review"] == 1
    assert summary.scopes_by_grade["4"] == 2
    assert summary.scopes_by_grade["5"] == 1
    assert summary.scopes_by_subject["math"] == 2
    assert summary.scopes_by_subject["sci"] == 1
    
    assert summary.global_summary.total_caps_refs == 3
    assert summary.global_summary.amber_refs == 3
    
    assert summary.global_layers[ContentLayer.LESSONS].target_total == 30
    assert summary.global_layers[ContentLayer.LESSONS].approved_total == 15
    assert summary.global_layers[ContentLayer.LESSONS].coverage_ratio == 0.5


@pytest.mark.asyncio
async def test_get_coverage_gap_report(mock_coverage_service):
    gap_report = await mock_coverage_service.get_coverage_gap_report(grade=4, layers=[ContentLayer.LESSONS])
    # grade 4 has 2 scopes. Each scope has 1 caps_ref with target 10, approved 5. (Gap 5).
    assert gap_report.total_gaps == 2
    assert len(gap_report.gaps) == 2
    assert gap_report.gaps[0].gap == 5
    assert gap_report.gaps[1].gap == 5
