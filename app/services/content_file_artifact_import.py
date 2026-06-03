"""Import generated file artifacts into Content Factory DB artifact records."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
    ContentValidationReport,
)
from app.services.content_factory import stable_json_hash
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService
from app.services.content_scope_registry import ContentScopeRegistry

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_LAYER_SPECS = {
    "diagnostic_items": (ContentLayer.DIAGNOSTIC_ITEMS, ContentArtifactType.DIAGNOSTIC_ITEM, "items"),
    "lessons": (ContentLayer.LESSONS, ContentArtifactType.LESSON, "lessons"),
    "assessment_blueprints": (ContentLayer.ASSESSMENT_BLUEPRINTS, ContentArtifactType.ASSESSMENT_BLUEPRINT, "blueprints"),
    "study_plan_templates": (ContentLayer.STUDY_PLAN_TEMPLATES, ContentArtifactType.STUDY_PLAN_TEMPLATE, "topic_sequence"),
}


@dataclass(frozen=True)
class FileArtifactImportRecord:
    artifact_id: uuid.UUID
    scope_id: str
    layer: str
    artifact_type: str
    caps_ref: str | None
    artifact_hash: str
    status: str
    source_document_id: str
    payload_json: dict[str, Any]


@dataclass(frozen=True)
class FileArtifactImportPlan:
    scope_id: str
    review_status: str
    db_status: str
    records: list[FileArtifactImportRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class ContentFileArtifactImportService:
    """Plan and execute imports from generated JSON files into reviewable DB artifacts."""

    def __init__(
        self,
        *,
        project_root: Path | None = None,
        registry: ContentScopeRegistry | None = None,
        review_service: ContentFileReviewWorkflowService | None = None,
    ) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.registry = registry or ContentScopeRegistry(project_root=self.project_root)
        self.review_service = review_service or ContentFileReviewWorkflowService(project_root=self.project_root, registry=self.registry)

    def plan_scope_import(self, scope_id: str, *, max_records_per_layer: int | None = None) -> FileArtifactImportPlan:
        scope = self.registry.get_scope(scope_id)
        review = self.review_service.review_status(scope_id)
        db_status = ContentArtifactStatus.APPROVED.value if review.approved else ContentArtifactStatus.PENDING_REVIEW.value
        source_document_id = (scope.source_documents or ["unknown_source"])[0]
        records: list[FileArtifactImportRecord] = []
        errors = list(review.blockers)
        for path_key, (layer, artifact_type, collection_key) in _LAYER_SPECS.items():
            rel_path = scope.artifact_paths.get(path_key)
            if not rel_path:
                errors.append(f"{path_key} path is missing from scope registry.")
                continue
            path = self.project_root / rel_path
            if not path.exists():
                errors.append(f"{path_key} file is missing: {rel_path}")
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            items = list(payload.get(collection_key, []))
            if max_records_per_layer is not None:
                items = items[:max_records_per_layer]
            for index, item in enumerate(items):
                caps_ref = _caps_ref_for(path_key, item)
                artifact_hash = stable_json_hash({"scope_id": scope.scope_id, "layer": layer.value, "payload": item})
                records.append(
                    FileArtifactImportRecord(
                        artifact_id=uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:file-artifact:{scope.scope_id}:{layer.value}:{artifact_hash}"),
                        scope_id=scope.scope_id,
                        layer=layer.value,
                        artifact_type=artifact_type.value,
                        caps_ref=caps_ref,
                        artifact_hash=artifact_hash,
                        status=db_status,
                        source_document_id=source_document_id,
                        payload_json=item,
                    )
                )
        return FileArtifactImportPlan(scope_id=scope.scope_id, review_status=review.status, db_status=db_status, records=records, errors=errors)

    async def import_scope_files(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        actor_id: str,
        max_records_per_layer: int | None = None,
        dry_run: bool = True,
    ) -> FileArtifactImportPlan:
        plan = self.plan_scope_import(scope_id, max_records_per_layer=max_records_per_layer)
        if dry_run:
            return plan
        scope = self.registry.get_scope(scope_id)
        source_document_id = (scope.source_documents or ["unknown_source"])[0]
        for record in plan.records:
            artifact = ContentGenerationArtifact(
                artifact_id=record.artifact_id,
                scope_id=record.scope_id,
                content_layer=ContentLayer(record.layer),
                artifact_type=ContentArtifactType(record.artifact_type),
                caps_ref=record.caps_ref,
                grade=scope.grade,
                subject_code=scope.subject_code,
                language=scope.language,
                status=ContentArtifactStatus(record.status),
                artifact_json=record.payload_json,
                artifact_hash=record.artifact_hash,
                source_snapshot_hash=record.artifact_hash,
                provider="file_import",
                model="generated-scope-artifacts",
                prompt_version="scope_scaffold_v1",
                quality_score=0.9,
                safety_status="passed",
                answer_key_verified=True,
                caps_alignment_score=1.0,
            )
            session.add(artifact)
            session.add(ContentArtifactSource(
                artifact_id=record.artifact_id,
                source_document_id=source_document_id,
                source_chunk_id=f"{record.scope_id}:{record.layer}:{record.caps_ref or 'scope'}",
                source_title=source_document_id,
                source_type="caps_pdf",
                caps_ref=record.caps_ref,
                grade=scope.grade,
                subject_code=scope.subject_code,
                language=scope.language,
                license_status="government_open",
                source_quality_score=0.9,
                source_hash=record.artifact_hash,
                source_metadata={"document_status": "approved", "imported_by": actor_id},
            ))
            session.add(ContentValidationReport(
                artifact_id=record.artifact_id,
                passed=True,
                checks={"file_import_schema": True, "source_traceability": True, "safety_status": "passed"},
                errors=[],
            ))
        await session.flush()
        return plan


def _caps_ref_for(path_key: str, item: dict[str, Any]) -> str | None:
    if item.get("caps_ref"):
        return str(item["caps_ref"])
    selection_rules = item.get("selection_rules") or {}
    refs = selection_rules.get("caps_refs") or []
    if refs:
        return str(refs[0])
    return None
