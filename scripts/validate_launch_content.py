#!/usr/bin/env python3
"""Validate Grade 4 Maths launch content artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.lessons.lesson_validator import LessonValidator
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService

LAUNCH_REFS = {"4.M.1.1", "4.M.1.2", "4.M.1.3"}


def load(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Fail if 40 approved items and 8 approved lessons per ref are not met.")
    args = parser.parse_args()

    topic_map = load(ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json")
    coverage = load(ROOT / "data" / "caps" / "launch_coverage_targets.json")
    generated_item_path = ROOT / "data" / "generated" / "items" / "grade4_maths_launch_item_bank.json"
    item_path = generated_item_path if generated_item_path.exists() else ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
    items = load(item_path).get("items", [])
    lessons = load(ROOT / "data" / "generated" / "lessons" / "grade4_maths_launch_lessons.json").get("lessons", [])
    blueprints = load(ROOT / "data" / "generated" / "assessment_blueprints" / "grade4_maths_launch_blueprints.json").get("blueprints", [])
    templates = load(ROOT / "data" / "generated" / "study_plans" / "grade4_maths_launch_templates.json")

    target_refs = {row["caps_ref"] for row in coverage.get("targets", [])}
    errors: list[str] = []
    if target_refs != LAUNCH_REFS:
        errors.append(f"coverage target refs mismatch: {sorted(target_refs)}")

    item_validator = ItemValidator(topic_map=topic_map)
    item_counts: Counter[str] = Counter()
    for item in items:
        if item.get("caps_ref") in LAUNCH_REFS:
            item_errors = item_validator.validate_all(item)
            if item_errors:
                errors.append(f"item {item.get('item_id')} failed: {[e.rule for e in item_errors]}")
            if item.get("review_status") == "approved":
                item_counts[item["caps_ref"]] += 1

    caps_service = CAPSTopicMapService()
    lesson_validator = LessonValidator(caps_service=caps_service)
    lesson_counts: Counter[str] = Counter()
    for lesson in lessons:
        if lesson.get("caps_ref") not in LAUNCH_REFS:
            errors.append(f"lesson {lesson.get('lesson_id')} has non-launch ref {lesson.get('caps_ref')}")
            continue
        result = lesson_validator.validate(lesson, require_verified=True)
        if not result.passed:
            errors.append(f"lesson {lesson.get('lesson_id')} failed: {result.failures}")
        if lesson.get("review_status") == "approved":
            lesson_counts[lesson["caps_ref"]] += 1

    for blueprint in blueprints:
        refs = set(blueprint.get("selection_rules", {}).get("caps_refs", []))
        if not refs or not refs <= LAUNCH_REFS:
            errors.append(f"blueprint {blueprint.get('blueprint_id')} refs invalid: {sorted(refs)}")

    template_refs = {row.get("caps_ref") for row in templates.get("topic_sequence", [])}
    if not LAUNCH_REFS <= template_refs:
        errors.append(f"study template missing refs: {sorted(LAUNCH_REFS - template_refs)}")

    if args.strict:
        for ref in LAUNCH_REFS:
            if item_counts[ref] < 40:
                errors.append(f"{ref} approved item target unmet: {item_counts[ref]}/40")
            if lesson_counts[ref] < 8:
                errors.append(f"{ref} approved lesson target unmet: {lesson_counts[ref]}/8")

    print("Launch content validation")
    print(f"  item source: {item_path}")
    print(f"  approved item counts: {dict(item_counts)}")
    print(f"  approved lesson counts: {dict(lesson_counts)}")
    print(f"  blueprints: {len(blueprints)}")
    print(f"  strict: {args.strict}")
    if errors:
        print("Failures:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("  status: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
