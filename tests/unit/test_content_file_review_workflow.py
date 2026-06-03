from __future__ import annotations

from pathlib import Path

import pytest

from app.services.content_file_artifact_import import ContentFileArtifactImportService
from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService

pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_pilot_review_packet_defaults_to_pending_educator_approval(tmp_path: Path) -> None:
    service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)

    packet = service.build_review_packet("grade5_mathematics_en")
    status = service.review_status("grade5_mathematics_en")

    assert packet["decision"] == "pending"
    assert status.approved is False
    assert "Educator review decision is not approved." in status.blockers
    assert packet["layer_review"]["diagnostic_items"]["record_count"] == 640


def test_approved_review_packet_requires_reviewer_url_and_timestamp(tmp_path: Path) -> None:
    service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)

    service.build_review_packet(
        "grade5_mathematics_en",
        reviewer_id="educator-1",
        decision="approved",
        evidence_url="https://review.example/grade5-maths",
        output_dir=tmp_path,
    )
    status = service.review_status("grade5_mathematics_en")

    assert status.approved is True
    assert status.blockers == []


def test_import_plan_uses_pending_review_until_educator_approval(tmp_path: Path) -> None:
    review_service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)
    review_service.build_review_packet("grade5_mathematics_en")
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT, review_service=review_service)

    plan = importer.plan_scope_import("grade5_mathematics_en", max_records_per_layer=2)

    assert plan.db_status == "pending_review"
    assert len(plan.records) == 8
    assert {record.layer for record in plan.records} == {
        "diagnostic_items",
        "lessons",
        "assessment_blueprints",
        "study_plan_templates",
    }


def test_import_plan_switches_to_approved_with_complete_review_evidence(tmp_path: Path) -> None:
    review_service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)
    review_service.build_review_packet(
        "grade5_mathematics_en",
        reviewer_id="educator-1",
        decision="approved",
        evidence_url="https://review.example/grade5-maths",
    )
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT, review_service=review_service)

    plan = importer.plan_scope_import("grade5_mathematics_en", max_records_per_layer=1)

    assert plan.db_status == "approved"
    assert len(plan.records) == 4
    assert not plan.errors


def test_promotion_readiness_reports_pilot_review_evidence() -> None:
    readiness = ContentFilePromotionReadinessService(project_root=REPO_ROOT).evaluate_scope("grade5_mathematics_en")

    assert readiness.staging_eligible is True
    assert readiness.production_eligible is False
    assert readiness.manifest["review_evidence"]["status"] == "pending"
    assert readiness.manifest["review_evidence"]["manifest_path"] == "data/generated/review_manifests/grade5_mathematics_en_educator_review.json"


class _ScalarResult:
    def __init__(self, value=None):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _ImportSession:
    def __init__(self):
        self.artifacts = {}
        self.sources = {}
        self.reports = {}
        self.added = []
        self.flush_count = 0

    async def get(self, model, key):
        return self.artifacts.get(key)

    async def execute(self, stmt):
        return _ScalarResult(None)

    def has_source_for_import(self, record):
        return (record.artifact_id, record.artifact_hash) in self.sources

    def has_validation_report_for_import(self, record):
        return record.artifact_id in self.reports

    def add(self, obj):
        self.added.append(obj)
        name = obj.__class__.__name__
        if name == "ContentGenerationArtifact":
            self.artifacts[obj.artifact_id] = obj
        elif name == "ContentArtifactSource":
            self.sources[(obj.artifact_id, obj.source_hash)] = obj
        elif name == "ContentValidationReport":
            self.reports[obj.artifact_id] = obj

    async def flush(self):
        self.flush_count += 1


@pytest.mark.asyncio
async def test_file_artifact_import_is_idempotent_for_pilot_scope(tmp_path: Path) -> None:
    review_service = ContentFileReviewWorkflowService(project_root=REPO_ROOT, manifest_dir=tmp_path)
    review_service.build_review_packet("grade5_mathematics_en")
    importer = ContentFileArtifactImportService(project_root=REPO_ROOT, review_service=review_service)
    session = _ImportSession()

    first = await importer.import_scope_files(
        session,
        "grade5_mathematics_en",
        actor_id="admin-1",
        max_records_per_layer=1,
        dry_run=False,
    )
    second = await importer.import_scope_files(
        session,
        "grade5_mathematics_en",
        actor_id="admin-1",
        max_records_per_layer=1,
        dry_run=False,
    )

    assert first.created_count == 4
    assert first.source_count == 4
    assert first.validation_report_count == 4
    assert second.created_count == 0
    assert second.updated_count == 4
    assert second.source_count == 0
    assert second.validation_report_count == 0
    assert len(session.artifacts) == 4
    assert len(session.sources) == 4
    assert len(session.reports) == 4
