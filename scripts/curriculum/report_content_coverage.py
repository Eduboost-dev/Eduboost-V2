#!/usr/bin/env python3
"""Report Content Factory study material coverage from the scope registry."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_scope import ContentScopeStatus
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_scope_content import validate_scope
from scripts.curriculum.validate_source_manifest import generation_ready
from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService


def build_report(
    *, 
    strict_counts: bool = False,
    grade: int | None = None,
    subject_code: str | None = None,
) -> dict[str, Any]:
    registry = ContentScopeRegistry()
    readiness_service = ContentFilePromotionReadinessService(registry=registry)
    rows: list[dict[str, Any]] = []
    totals: dict[str, int] = defaultdict(int)

    for scope in registry.list_scopes():
        if grade is not None and scope.grade != grade:
            continue
        if subject_code is not None and scope.subject_code != subject_code:
            continue
            
        active = scope.status == ContentScopeStatus.ACTIVE
        validation = validate_scope(scope.scope_id, strict=strict_counts, registry=registry) if active else None
        target_rows = (
            registry.get_scope_targets(scope.scope_id)
            if scope.status in {ContentScopeStatus.ACTIVE, ContentScopeStatus.GENERATING, ContentScopeStatus.REVIEW}
            else []
        )
        layer_targets = defaultdict(int)
        for target in target_rows:
            for key, value in target.targets.items():
                layer_targets[key] += int(value)

        readiness = readiness_service.evaluate_scope(scope.scope_id)
        total_target = sum(layer_targets.values())
        total_approved = 0
        for layer_name, layer_data in readiness.manifest["layers"].items():
            if f"{layer_name}.approved" in layer_targets:
                total_approved += int(layer_data["record_count"])
        coverage_ratio = (total_approved / total_target * 100) if total_target > 0 else 100.0

        row = {
            "scope_id": scope.scope_id,
            "grade": scope.grade,
            "phase": scope.phase,
            "subject_code": scope.subject_code,
            "subject": scope.subject,
            "language": scope.language,
            "status": scope.status.value,
            "learner_visible": active,
            "generation_ready": generation_ready(scope.scope_id, registry=registry),
            "caps_ref_count": len(scope.caps_refs),
            "target_counts": dict(sorted(layer_targets.items())),
            "coverage_percentage": coverage_ratio,
            "validation_status": "not_applicable" if not active else ("ok" if validation and validation.passed else "failed"),
            "errors": [] if validation is None else validation.errors,
            "artifact_layers": readiness.manifest["layers"],
            "staging_eligible": readiness.staging_eligible,
            "production_eligible": readiness.production_eligible,
            "promotion_blockers": readiness.blockers,
        }
        rows.append(row)
        totals[f"scopes.{scope.status.value}"] += 1
        if row["generation_ready"]:
            totals["scopes.generation_ready"] += 1
        if readiness.staging_eligible:
            totals["scopes.staging_eligible"] += 1
        if readiness.production_eligible:
            totals["scopes.production_eligible"] += 1
        for layer_name, layer_data in readiness.manifest["layers"].items():
            if layer_data["exists"]:
                totals[f"layers.{layer_name}.files_present"] += 1
            totals[f"layers.{layer_name}.records"] += int(layer_data["record_count"])
        if active:
            totals["scopes.learner_visible"] += 1
            totals["caps_refs.active"] += len(scope.caps_refs)
        else:
            totals["scopes.not_learner_visible"] += 1

    return {
        "schema_version": "1.0",
        "summary": dict(sorted(totals.items())),
        "scopes": rows,
    }


def print_text(report: dict[str, Any]) -> None:
    print("Study material coverage")
    for key, value in report["summary"].items():
        print(f"  {key}: {value}")
    print("\nScopes")
    for row in report["scopes"]:
        visible = "learner-visible" if row["learner_visible"] else "not learner-visible"
        ready = "generation-ready" if row["generation_ready"] else "not generation-ready"
        print(
            f"  {row['scope_id']}: {row['status']} ({visible}, {ready}), "
            f"caps_refs={row['caps_ref_count']}, validation={row['validation_status']}, "
            f"staging={row['staging_eligible']}, production={row['production_eligible']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--strict-counts", action="store_true", help="Run strict count validation for active scopes.")
    parser.add_argument("--grade", type=int, help="Filter by grade")
    parser.add_argument("--subject-code", type=str, help="Filter by subject code")
    parser.add_argument("--alert-threshold", type=float, default=80.0, help="Fail if any active scope coverage ratio drops below this percentage (default: 80.0)")
    parser.add_argument("--ci-summary", action="store_true", help="Write a CI-friendly JSON summary to data/generated/coverage_reports/ci_coverage_summary.json")
    args = parser.parse_args()

    report = build_report(
        strict_counts=args.strict_counts,
        grade=args.grade,
        subject_code=args.subject_code,
    )
    
    if args.ci_summary:
        out_dir = ROOT / "data" / "generated" / "coverage_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ci_coverage_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text(report)
        
    failed = [row for row in report["scopes"] if row["validation_status"] == "failed"]
    below_threshold = [
        row for row in report["scopes"] 
        if row["status"] == "active" and row["coverage_percentage"] < args.alert_threshold
    ]
    
    if below_threshold:
        print(f"\nERROR: {len(below_threshold)} active scope(s) below coverage threshold ({args.alert_threshold}%):", file=sys.stderr)
        for row in below_threshold:
            print(f"  - {row['scope_id']} ({row['coverage_percentage']:.1f}%)", file=sys.stderr)
            
    return 1 if (failed or below_threshold) else 0


if __name__ == "__main__":
    raise SystemExit(main())