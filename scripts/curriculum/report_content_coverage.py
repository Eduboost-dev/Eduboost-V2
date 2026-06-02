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

from app.domain.content_coverage import ContentLayer
from app.domain.content_scope import ContentScopeStatus
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_scope_content import validate_scope


def build_report(*, strict_counts: bool = False) -> dict[str, Any]:
    registry = ContentScopeRegistry()
    rows: list[dict[str, Any]] = []
    totals: dict[str, int] = defaultdict(int)

    for scope in registry.list_scopes():
        active = scope.status == ContentScopeStatus.ACTIVE
        validation = validate_scope(scope.scope_id, strict=strict_counts, registry=registry) if active else None
        target_rows = registry.get_scope_targets(scope.scope_id) if active else []
        layer_targets = defaultdict(int)
        for target in target_rows:
            for key, value in target.targets.items():
                layer_targets[key] += int(value)

        row = {
            "scope_id": scope.scope_id,
            "grade": scope.grade,
            "phase": scope.phase,
            "subject_code": scope.subject_code,
            "subject": scope.subject,
            "language": scope.language,
            "status": scope.status.value,
            "learner_visible": active,
            "caps_ref_count": len(scope.caps_refs),
            "target_counts": dict(sorted(layer_targets.items())),
            "validation_status": "not_applicable" if not active else ("ok" if validation and validation.passed else "failed"),
            "errors": [] if validation is None else validation.errors,
        }
        rows.append(row)
        totals[f"scopes.{scope.status.value}"] += 1
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
        print(
            f"  {row['scope_id']}: {row['status']} ({visible}), "
            f"caps_refs={row['caps_ref_count']}, validation={row['validation_status']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--strict-counts", action="store_true", help="Run strict count validation for active scopes.")
    args = parser.parse_args()

    report = build_report(strict_counts=args.strict_counts)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text(report)
    failed = [row for row in report["scopes"] if row["validation_status"] == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())