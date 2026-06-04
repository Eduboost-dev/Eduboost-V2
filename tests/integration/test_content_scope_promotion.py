from __future__ import annotations

from pathlib import Path

from unittest.mock import patch, MagicMock
import pytest

from app.models.content_factory import (
    ContentArtifactSource,
    ContentGenerationArtifact,
    ContentValidationReport,
)
from app.services.content_file_artifact_import import ContentFileArtifactImportService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService
from app.services.content_scope_registry import ContentScopeRegistry

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def integration_db():
    pass


class _ImportSession:
    def __init__(self) -> None:
        self.artifacts: dict[object, ContentGenerationArtifact] = {}
        self.sources: set[tuple[object, str]] = set()
        self.validation_reports: set[object] = set()

    async def get(self, model, key):
        if model is ContentGenerationArtifact:
            return self.artifacts.get(key)
        return None

    async def execute(self, stmt):
        class _EmptyResult:
            def scalar_one_or_none(self):
                return None

        return _EmptyResult()

    def add(self, obj) -> None:
        if isinstance(obj, ContentGenerationArtifact):
            self.artifacts[obj.artifact_id] = obj
        elif isinstance(obj, ContentArtifactSource):
            self.sources.add((obj.artifact_id, obj.source_hash))
        elif isinstance(obj, ContentValidationReport):
            self.validation_reports.add(obj.artifact_id)

    async def flush(self) -> None:
        return None

    def has_source_for_import(self, record) -> bool:
        return (record.artifact_id, record.artifact_hash) in self.sources

    def has_validation_report_for_import(self, record) -> bool:
        return record.artifact_id in self.validation_reports


def test_dev_approved_scope_is_not_learner_visible() -> None:
    registry = ContentScopeRegistry()

    review_scope = registry.get_scope("grade5_mathematics_en")

    assert review_scope.status.value == "review"
    assert registry.is_scope_active("grade5_mathematics_en") is False
    assert "grade5_mathematics_en" not in {scope.scope_id for scope in registry.list_active_scopes()}


def test_production_promotion_requires_educator_and_legal_approval() -> None:
    review_status = ContentFileReviewWorkflowService(project_root=REPO_ROOT).review_status(
        "grade6_mathematics_en"
    )

    assert review_status.status == "dev_approved"
    assert review_status.stage_unlocked is True
    assert review_status.production_unlocked is False
    blockers = " ".join(review_status.production_blockers)
    assert "Educator approval is required for production" in blockers
    assert "Legal approval is required for production" in blockers


@pytest.mark.asyncio
async def test_import_plan_is_idempotent() -> None:
    service = ContentFileArtifactImportService(project_root=REPO_ROOT)
    session = _ImportSession()

    first = await service.import_scope_files(
        session,
        "grade6_mathematics_en",
        actor_id="test-importer",
        max_records_per_layer=1,
        dry_run=False,
    )
    second = await service.import_scope_files(
        session,
        "grade6_mathematics_en",
        actor_id="test-importer",
        max_records_per_layer=1,
        dry_run=False,
    )

    assert first.created_count == len(first.records)
    assert first.updated_count == 0
    assert second.created_count == 0
    assert second.updated_count == len(second.records)
    assert {record.artifact_id for record in first.records} == {record.artifact_id for record in second.records}
    assert len(session.artifacts) == len(first.records)


def test_promotion_blocked_when_lesson_quality_fails() -> None:
    from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
    from app.services.content_file_lesson_quality import LessonFileQualityResult
    
    registry = ContentScopeRegistry()
    service = ContentFilePromotionReadinessService(project_root=REPO_ROOT, registry=registry)
    
    mock_audit = LessonFileQualityResult(
        scope_id="grade6_mathematics_en",
        relative_path="lessons.json",
        exists=True,
        passed=False,
        quarantined=True,
        lesson_count=10,
        failed_lesson_count=2,
        blockers=["Lesson quality audit failed"],
        aggregate={},
        issues=[]
    )
    
    with patch("app.services.content_file_lesson_quality.ContentFileLessonQualityService.audit_scope", return_value=mock_audit):
        result = service.evaluate_scope("grade6_mathematics_en")
        
        assert not result.staging_eligible
        assert not result.production_eligible
        assert "Lesson quality audit failed" in result.blockers


def test_promotion_blocked_when_source_manifest_fails() -> None:
    from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
    
    registry = ContentScopeRegistry()
    service = ContentFilePromotionReadinessService(project_root=REPO_ROOT, registry=registry)
    
    with patch("app.services.content_file_promotion_readiness.generation_ready", return_value=False):
        result = service.evaluate_scope("grade6_mathematics_en")
        
        assert not result.staging_eligible
        assert not result.production_eligible
        assert "Scope source material is not generation-ready." in result.blockers
