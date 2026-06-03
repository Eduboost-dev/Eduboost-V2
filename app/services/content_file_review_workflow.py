"""File-backed educator review workflow for generated scope artifacts."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from typing import TYPE_CHECKING

from app.services.content_scope_registry import ContentScopeRegistry

if TYPE_CHECKING:
    from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_MANIFEST_DIR = PROJECT_ROOT / "data" / "generated" / "review_manifests"


@dataclass(frozen=True)
class ScopeReviewEvidenceStatus:
    scope_id: str
    status: str
    approved: bool
    blockers: list[str]
    manifest_path: Path | None
    manifest: dict[str, Any] | None


class ContentFileReviewWorkflowService:
    """Create and verify educator review evidence for generated scope files."""

    def __init__(
        self,
        *,
        project_root: Path | None = None,
        registry: ContentScopeRegistry | None = None,
        readiness_service: "ContentFilePromotionReadinessService | None" = None,
        manifest_dir: Path | None = None,
    ) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.registry = registry or ContentScopeRegistry(project_root=self.project_root)
        self.manifest_dir = manifest_dir or REVIEW_MANIFEST_DIR
        if readiness_service is None:
            from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService

            readiness_service = ContentFilePromotionReadinessService(
                project_root=self.project_root,
                registry=self.registry,
                review_service=self,
            )
        self.readiness_service = readiness_service

    def build_review_packet(
        self,
        scope_id: str,
        *,
        reviewer_id: str = "pending",
        decision: str = "pending",
        evidence_url: str = "pending",
        notes: str = "Educator review not yet completed.",
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        scope = self.registry.get_scope(scope_id)
        readiness = self.readiness_service.evaluate_scope(scope_id).manifest
        approved_at = _now_utc() if _approved_decision(decision) and reviewer_id != "pending" and evidence_url != "pending" else None
        packet = {
            "schema_version": "1.0",
            "generated_at": _now_utc(),
            "scope_id": scope.scope_id,
            "scope_status": scope.status.value,
            "review_policy_id": scope.review_policy_id,
            "decision": decision,
            "approved": _approved_decision(decision),
            "reviewer_id": reviewer_id,
            "evidence_url": evidence_url,
            "approved_at": approved_at,
            "notes": notes,
            "layer_review": {
                layer: {
                    "path": data["relative_path"],
                    "sha256": data["sha256"],
                    "record_count": data["record_count"],
                    "review_ready_count": data["review_ready_count"],
                    "review_status": "approved" if _approved_decision(decision) else "pending_educator_review",
                }
                for layer, data in readiness["layers"].items()
            },
            "promotion_readiness": {
                "staging_eligible": readiness["staging_eligible"],
                "production_eligible": readiness["production_eligible"],
                "blockers": readiness["blockers"],
            },
        }
        output_dir = output_dir or self.manifest_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{scope_id}_educator_review.json"
        _write_json(path, packet)
        return packet

    def review_status(self, scope_id: str, *, manifest_dir: Path | None = None) -> ScopeReviewEvidenceStatus:
        manifest_dir = manifest_dir or self.manifest_dir
        path = manifest_dir / f"{scope_id}_educator_review.json"
        if not path.exists():
            return ScopeReviewEvidenceStatus(scope_id, "missing", False, ["Educator review evidence packet is missing."], None, None)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        blockers: list[str] = []
        if not _approved_decision(manifest.get("decision")):
            blockers.append("Educator review decision is not approved.")
        if _pending(manifest.get("reviewer_id")):
            blockers.append("Educator reviewer_id is pending.")
        if _pending(manifest.get("evidence_url")):
            blockers.append("Educator review evidence_url is pending.")
        if _pending(manifest.get("approved_at")):
            blockers.append("Educator approved_at timestamp is pending.")
        if manifest.get("scope_id") != scope_id:
            blockers.append("Educator review packet scope_id does not match request.")
        for layer, data in (manifest.get("layer_review") or {}).items():
            if int(data.get("record_count") or 0) <= 0:
                blockers.append(f"{layer} review packet has no records.")
            if not data.get("sha256"):
                blockers.append(f"{layer} review packet is missing artifact hash.")
        return ScopeReviewEvidenceStatus(
            scope_id=scope_id,
            status="approved" if not blockers else "pending",
            approved=not blockers,
            blockers=blockers,
            manifest_path=path,
            manifest=manifest,
        )


def _approved_decision(value: Any) -> bool:
    return str(value or "").strip().lower() in {"approved", "approve", "accepted", "pass", "passed"}


def _pending(value: Any) -> bool:
    return value is None or str(value).strip().lower() in {"", "pending", "none", "null"}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
