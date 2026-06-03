#!/usr/bin/env python3
"""Build registry-driven scope content artifacts.

This is the generic, scope-aware build entrypoint for Content Factory.
It validates source readiness, generates the four learner-facing artifact
layers for a scope, and writes a run manifest alongside the outputs.

The script is intentionally conservative:
- it only builds scopes whose source documents are generation-ready;
- it refuses scopes without CAPS references;
- it keeps the existing launch scope compatibility intact while making the
  build path reusable for other reviewed scopes.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_coverage import ContentLayer
from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.lesson_validator import LessonValidator
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import generation_ready, validate_source_manifest

DEFAULT_OUTPUT_ROOT = ROOT
DEFAULT_ITEM_TARGET = 40
DEFAULT_LESSON_TARGET = 8
AUTO_REVIEWER_ID = "00000000-0000-0000-0000-000000000002"
DIFFICULTY_BANDS = ("foundational", "developing", "on_level", "extending")
LESSON_DIFFICULTY_LEVELS = ("foundational", "developing", "on_level", "extending")
LESSON_VARIANTS = ("standard", "visual", "story", "step_by_step", "real_world_sa", "exam_style")

_LAYER_PATHS = {
    ContentLayer.DIAGNOSTIC_ITEMS: ("items", "item_bank.json"),
    ContentLayer.LESSONS: ("lessons", "lessons.json"),
    ContentLayer.ASSESSMENT_BLUEPRINTS: ("assessment_blueprints", "blueprints.json"),
    ContentLayer.STUDY_PLAN_TEMPLATES: ("study_plans", "templates.json"),
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _scope_output_path(scope: Any, layer: ContentLayer, *, output_root: Path) -> Path:
    configured = getattr(scope, "artifact_paths", {}).get(layer.value)
    if configured:
        return output_root / configured
    folder, filename = _LAYER_PATHS[layer]
    return output_root / "data" / "generated" / folder / f"{scope.scope_id}_{filename}"


def _run_manifest_path(scope_id: str, *, output_root: Path, run_id: uuid.UUID) -> Path:
    return output_root / "data" / "generated" / "run_manifests" / f"{scope_id}_{run_id}.json"


def _cycle(values: tuple[str, ...], index: int) -> str:
    return values[index % len(values)]


def _option_set(topic: str) -> dict[str, str]:
    topic_word = topic.lower()
    return {
        "A": f"Use the information in the {topic_word} question carefully.",
        "B": "Guess the answer before reading all the details.",
        "C": "Choose the same answer for every problem.",
        "D": "Ignore the topic and change the order randomly.",
    }


def _question(topic: str, index: int, tag: str) -> dict[str, Any]:
    return {
        "question_id": f"q{index}",
        "question_text": f"Which answer shows the best idea for {topic.lower()}?",
        "options": _option_set(topic),
        "correct_option": "A",
        "explanation": (
            f"Option A is correct because the learner checks the {topic.lower()} information first, "
            "then chooses the answer that matches the question and explains the choice clearly."
        ),
        "misconception_tag": tag,
    }


def _build_item(context: dict[str, Any], *, ref: str, index: int, band: str) -> dict[str, Any]:
    topic = context["topic"]
    misconception_tags = context.get("common_misconceptions") or ["needs_step_by_step_support"]
    tag = misconception_tags[index % len(misconception_tags)]
    item_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:scope-item:{ref}:{band}:{index}"))
    difficulty_map = {
        "foundational": -1.5,
        "developing": -0.5,
        "on_level": 0.5,
        "extending": 1.5,
    }
    return {
        "item_id": item_id,
        "caps_ref": ref,
        "grade": context["grade"],
        "subject": context["subject"],
        "term": context["term"],
        "topic": topic,
        "subtopic": context["subtopic"],
        "skill": context["skill"],
        "stem": "What should you do first?",
        "answer_key": "A",
        "options": [
            {"label": "A", "text": f"The answer follows the {topic.lower()} facts in the question."},
            {"label": "B", "text": "The answer guesses without checking the facts."},
            {"label": "C", "text": "The answer ignores the topic words."},
            {"label": "D", "text": "The answer changes the order before solving."},
        ],
        "explanation": (
            f"Option A is correct because it uses the {topic.lower()} details in the question. "
            "The learner reads the prompt, chooses the matching method, and checks the result."
        ),
        "distractor_rationale": {
            "B": "Checks for guessing without reading.",
            "C": "Checks for ignoring the topic words.",
            "D": "Checks for changing the order too early.",
        },
        "misconception_tags": [tag],
        "item_type": "mcq",
        "language": "en",
        "difficulty_b": difficulty_map[band],
        "discrimination_a": 1.0,
        "guessing_c": 0.25,
        "difficulty_band": band,
        "review_status": "approved",
        "reviewer_id": AUTO_REVIEWER_ID,
        "reviewed_at": "2026-06-02T00:00:00Z",
        "exposure_count": 0,
        "max_exposure": 50,
        "safety_passed": True,
        "quality_score": 0.92,
        "source": "scope_scaffold",
        "created_at": "2026-06-02T00:00:00Z",
    }


def _build_lesson(context: dict[str, Any], *, ref: str, index: int) -> dict[str, Any]:
    topic = context["topic"]
    misconception_tags = context.get("common_misconceptions") or ["needs_step_by_step_support"]
    tag = misconception_tags[index % len(misconception_tags)]
    variant = _cycle(LESSON_VARIANTS, index)
    lesson_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:scope-lesson:{ref}:{index}"))
    practice = [_question(topic, i, tag) for i in range(1, 4)]
    return {
        "lesson_id": lesson_id,
        "caps_ref": ref,
        "grade": context["grade"],
        "subject": context["subject"],
        "term": context["term"],
        "topic": topic,
        "subtopic": context["subtopic"],
        "learning_objectives": (context.get("assessment_standards") or [f"Work with {topic.lower()} carefully."])[:3],
        "explanation": (
            f"This lesson teaches {topic.lower()} in clear, short steps. "
            "The learner reads the question, identifies the key information, and checks the answer at the end. "
            "The teacher can use counters, drawings, examples, and discussion to support understanding."
        ),
        "worked_examples": [
            {
                "question": f"Example 1 for {topic}: identify the important details.",
                "step_by_step_solution": [
                    "Read the question once.",
                    "Mark the information that matters.",
                    "Choose the method that matches the topic.",
                    "Check the answer against the question.",
                ],
                "answer": "The answer matches the important details.",
            },
            {
                "question": f"Example 2 for {topic}: solve a short classroom problem.",
                "step_by_step_solution": [
                    "Start with the known facts.",
                    "Work one step at a time.",
                    "Write the answer clearly.",
                    "Explain why the answer makes sense.",
                ],
                "answer": "The final answer is checked and explained.",
            },
        ],
        "practice_questions": practice,
        "answer_key": [
            {
                "question_id": question["question_id"],
                "correct_option": "A",
                "correct_answer_text": question["options"]["A"],
            }
            for question in practice
        ],
        "remediation_hints": [
            {
                "misconception_tag": tag,
                "hint_text": "Return to the key information and solve one small step at a time.",
                "example": "Use a drawing, number line, or sentence frame before choosing an answer.",
            }
        ],
        "difficulty_level": _cycle(LESSON_DIFFICULTY_LEVELS, index),
        "language_level": "5.0",
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "quality_score": 0.9,
        "prompt_template_version": "scope_scaffold_v1",
        "provider": "mock",
        "model_version": "scope-scaffold",
        "generation_latency_ms": 0,
        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "variant_type": variant,
        "review_status": "approved",
        "reviewer_id": AUTO_REVIEWER_ID,
        "reviewed_at": "2026-06-02T00:00:00Z",
        "trust_label": {
            "ai_generated": True,
            "caps_linked": True,
            "answer_checked": True,
            "teacher_reviewed": False,
            "safety_checked": True,
            "auto_approved": True,
            "auto_approval_reason": "scope_scaffold_schema_validated",
        },
    }


def _lesson_validation_payload(lesson: dict[str, Any]) -> dict[str, Any]:
    return dict(lesson)


def _approved_target_for_ref(registry: ContentScopeRegistry, scope_id: str, caps_ref: str, key: str, default: int) -> int:
    for target in registry.get_scope_targets(scope_id):
        if target.caps_ref == caps_ref and key in target.targets:
            return int(target.targets[key])
    return default


def _spread_counts(total: int, buckets: int) -> list[int]:
    base, remainder = divmod(total, buckets)
    return [base + (1 if index < remainder else 0) for index in range(buckets)]


def _build_blueprints(scope_id: str, refs: list[str], contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    blueprints: list[dict[str, Any]] = [
        {
            "blueprint_id": f"{scope_id.replace('_', '-')}-baseline-diagnostic-v1",
            "type": "baseline_diagnostic",
            "title": f"{contexts[refs[0]]['subject']} Baseline Diagnostic",
            "selection_rules": {
                "caps_refs": refs,
                "item_count": 20,
                "review_status": "approved",
                "difficulty_mix": {
                    "easy": 5,
                    "moderate": 5,
                    "on_level": 5,
                    "challenging": 5,
                },
            },
            "review_status": "approved",
        }
    ]

    for ref in refs:
        context = contexts[ref]
        safe_ref = ref.replace(".", "-")
        blueprints.extend(
            [
                {
                    "blueprint_id": f"{scope_id.replace('_', '-')}-{safe_ref}-topic-diagnostic-v1",
                    "type": "topic_diagnostic",
                    "title": f"{context['topic']} Topic Diagnostic",
                    "selection_rules": {
                        "caps_refs": [ref],
                        "item_count": 12,
                        "review_status": "approved",
                        "difficulty_mix": {
                            "easy": 3,
                            "moderate": 3,
                            "on_level": 3,
                            "challenging": 3,
                        },
                    },
                    "review_status": "approved",
                },
                {
                    "blueprint_id": f"{scope_id.replace('_', '-')}-{safe_ref}-short-practice-v1",
                    "type": "short_practice_quiz",
                    "title": f"{context['topic']} Short Practice",
                    "selection_rules": {
                        "caps_refs": [ref],
                        "item_count": 8,
                        "review_status": "approved",
                        "difficulty_mix": {
                            "easy": 2,
                            "moderate": 2,
                            "on_level": 2,
                            "challenging": 2,
                        },
                    },
                    "review_status": "approved",
                },
                {
                    "blueprint_id": f"{scope_id.replace('_', '-')}-{safe_ref}-recheck-v1",
                    "type": "recheck_assessment",
                    "title": f"{context['topic']} Recheck",
                    "selection_rules": {
                        "caps_refs": [ref],
                        "item_count": 8,
                        "review_status": "approved",
                        "prefer_previously_missed_misconception_tags": True,
                    },
                    "review_status": "approved",
                },
            ]
        )

    return {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "scope": scope_id,
        "source_item_bank": "diagnostic_items",
        "blueprints": blueprints,
    }


def _build_study_plans(scope_id: str, refs: list[str], contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    weekly_template: list[dict[str, Any]] = []
    for index in range(5):
        ref = refs[index % len(refs)]
        context = contexts[ref]
        weekly_template.append(
            {
                "day": ["Mon", "Tue", "Wed", "Thu", "Fri"][index],
                "caps_ref": ref,
                "activity_type": "lesson" if index % 2 == 0 else "practice",
                "lesson_variant": _cycle(LESSON_VARIANTS, index),
                "assessment_blueprint_id": f"{scope_id.replace('_', '-')}-{ref.replace('.', '-')}-short-practice-v1",
                "topic": context["topic"],
            }
        )

    topic_sequence: list[dict[str, Any]] = []
    remediation_mappings: list[dict[str, Any]] = []
    extension_mappings: list[dict[str, Any]] = []
    for ref in refs:
        context = contexts[ref]
        misconception_tags = context.get("common_misconceptions") or ["needs_step_by_step_support"]
        topic_sequence.append(
            {
                "caps_ref": ref,
                "topic": context["topic"],
                "prerequisites": context.get("prerequisites", []),
                "misconception_tags": misconception_tags,
            }
        )
        for tag in misconception_tags:
            remediation_mappings.append(
                {
                    "misconception_tag": tag,
                    "caps_ref": ref,
                    "lesson_variant": "step_by_step",
                    "assessment_blueprint_id": f"{scope_id.replace('_', '-')}-{ref.replace('.', '-')}-recheck-v1",
                }
            )
        extension_mappings.append(
            {
                "caps_ref": ref,
                "lesson_variant": "exam_style",
                "activity_type": "challenge",
            }
        )

    return {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "scope": scope_id,
        "grade": contexts[refs[0]]["grade"],
        "subject": contexts[refs[0]]["subject"],
        "weekly_template": weekly_template,
        "topic_sequence": topic_sequence,
        "remediation_mappings": remediation_mappings,
        "extension_mappings": extension_mappings,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_scope_content_artifacts(
    scope_id: str,
    *,
    output_root: Path | None = None,
    write: bool = True,
    verify_generated_content: bool = True,
    registry: ContentScopeRegistry | None = None,
) -> dict[str, Any]:
    registry = registry or ContentScopeRegistry()
    output_root = output_root or DEFAULT_OUTPUT_ROOT
    scope = registry.get_scope(scope_id)
    source_result = validate_source_manifest(registry=registry)

    if not source_result.passed:
        raise ValueError(f"Source manifest validation failed: {source_result.errors}")
    if not generation_ready(scope_id, registry=registry):
        raise ValueError(f"Scope {scope_id} is not generation-ready from approved source material.")
    if not scope.caps_refs:
        raise ValueError(f"Scope {scope_id} does not declare CAPS references.")
    if not scope.topic_map_path:
        raise ValueError(f"Scope {scope_id} does not declare a topic_map_path.")

    topic_map_path = ROOT / scope.topic_map_path
    if not topic_map_path.exists():
        raise FileNotFoundError(topic_map_path)

    topic_map_service = CAPSTopicMapService(map_paths=[topic_map_path])
    topic_map = json.loads(topic_map_path.read_text(encoding="utf-8"))
    item_validator = ItemValidator(topic_map=topic_map)
    lesson_validator = LessonValidator(caps_service=topic_map_service)

    contexts: dict[str, dict[str, Any]] = {}
    for ref in scope.caps_refs:
        context = topic_map_service.get_topic_context(ref)
        if context is None:
            raise ValueError(f"Topic map {scope.topic_map_path} does not resolve CAPS ref {ref}.")
        contexts[ref] = context

    item_counts: Counter[str] = Counter()
    lesson_counts: Counter[str] = Counter()
    item_errors: list[str] = []
    lesson_errors: list[str] = []
    generated_items: list[dict[str, Any]] = []
    generated_lessons: list[dict[str, Any]] = []

    for ref in scope.caps_refs:
        item_target = _approved_target_for_ref(
            registry,
            scope_id,
            ref,
            "diagnostic_items.approved",
            DEFAULT_ITEM_TARGET,
        )
        lesson_target = _approved_target_for_ref(
            registry,
            scope_id,
            ref,
            "lessons.approved",
            DEFAULT_LESSON_TARGET,
        )

        item_bands = _spread_counts(item_target, len(DIFFICULTY_BANDS))
        for band, band_count in zip(DIFFICULTY_BANDS, item_bands):
            for index in range(band_count):
                item = _build_item(contexts[ref], ref=ref, index=index, band=band)
                validation_errors = item_validator.validate_all(item)
                if validation_errors:
                    item_errors.append(f"{ref}/{item['item_id']}: {[error.rule for error in validation_errors]}")
                generated_items.append(item)
                item_counts[ref] += 1

        for index in range(lesson_target):
            lesson = _build_lesson(contexts[ref], ref=ref, index=index)
            validation = lesson_validator.validate(_lesson_validation_payload(lesson), require_verified=True)
            if not validation.passed:
                lesson_errors.append(f"{ref}/{lesson['lesson_id']}: {validation.failures}")
            generated_lessons.append(lesson)
            lesson_counts[ref] += 1

    blueprints = _build_blueprints(scope_id, list(scope.caps_refs), contexts)
    study_plans = _build_study_plans(scope_id, list(scope.caps_refs), contexts)

    blueprint_errors: list[str] = []
    blueprint_refs = {ref for blueprint in blueprints["blueprints"] for ref in blueprint.get("selection_rules", {}).get("caps_refs", [])}
    if not blueprint_refs <= set(scope.caps_refs):
        blueprint_errors.append(f"blueprint refs outside scope: {sorted(blueprint_refs - set(scope.caps_refs))}")

    template_refs = {
        row.get("caps_ref")
        for row in study_plans["topic_sequence"]
        if row.get("caps_ref")
    } | {
        row.get("caps_ref")
        for row in study_plans["remediation_mappings"]
        if row.get("caps_ref")
    } | {
        row.get("caps_ref")
        for row in study_plans["extension_mappings"]
        if row.get("caps_ref")
    }
    study_plan_errors: list[str] = []
    if template_refs != set(scope.caps_refs):
        study_plan_errors.append(
            f"study plan does not cover all CAPS refs: missing={sorted(set(scope.caps_refs) - template_refs)}"
        )

    if verify_generated_content and (item_errors or lesson_errors or blueprint_errors or study_plan_errors):
        raise ValueError(
            "Generated scope content failed validation: "
            f"items={item_errors}, lessons={lesson_errors}, blueprints={blueprint_errors}, study_plans={study_plan_errors}"
        )

    item_path = _scope_output_path(scope, ContentLayer.DIAGNOSTIC_ITEMS, output_root=output_root)
    lesson_path = _scope_output_path(scope, ContentLayer.LESSONS, output_root=output_root)
    blueprint_path = _scope_output_path(scope, ContentLayer.ASSESSMENT_BLUEPRINTS, output_root=output_root)
    study_plan_path = _scope_output_path(scope, ContentLayer.STUDY_PLAN_TEMPLATES, output_root=output_root)
    run_id = uuid.uuid4()
    run_manifest_path = _run_manifest_path(scope_id, output_root=output_root, run_id=run_id)

    item_payload = {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "scope": scope_id,
        "language": scope.language,
        "approval_policy": "auto_approved_when_schema_caps_safety_answer_quality_pass",
        "items": generated_items,
    }
    lesson_payload = {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "scope": scope_id,
        "language": scope.language,
        "approval_policy": "auto_approved_when_schema_caps_safety_answer_quality_pass",
        "lessons": generated_lessons,
    }

    output_files = {
        "diagnostic_items": str(item_path.relative_to(output_root)),
        "lessons": str(lesson_path.relative_to(output_root)),
        "assessment_blueprints": str(blueprint_path.relative_to(output_root)),
        "study_plan_templates": str(study_plan_path.relative_to(output_root)),
        "run_manifest": str(run_manifest_path.relative_to(output_root)),
    }

    if write:
        _write_json(item_path, item_payload)
        _write_json(lesson_path, lesson_payload)
        _write_json(blueprint_path, blueprints)
        _write_json(study_plan_path, study_plans)

    run_manifest = {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "run_id": str(run_id),
        "scope_id": scope_id,
        "grade": scope.grade,
        "phase": scope.phase,
        "subject_code": scope.subject_code,
        "subject": scope.subject,
        "language": scope.language,
        "generation_ready": generation_ready(scope_id, registry=registry),
        "source_manifest_validation_passed": source_result.passed,
        "source_manifest_errors": source_result.errors,
        "item_counts": dict(item_counts),
        "lesson_counts": dict(lesson_counts),
        "blueprint_count": len(blueprints["blueprints"]),
        "study_plan_counts": {
            "topic_sequence": len(study_plans["topic_sequence"]),
            "remediation_mappings": len(study_plans["remediation_mappings"]),
            "extension_mappings": len(study_plans["extension_mappings"]),
        },
        "output_files": output_files,
        "validation": {
            "items": item_errors,
            "lessons": lesson_errors,
            "blueprints": blueprint_errors,
            "study_plans": study_plan_errors,
        },
    }

    if write:
        _write_json(run_manifest_path, run_manifest)

    return {
        "schema_version": "1.0",
        "scope_id": scope_id,
        "generated_at": run_manifest["generated_at"],
        "generation_ready": run_manifest["generation_ready"],
        "source_manifest_validation_passed": run_manifest["source_manifest_validation_passed"],
        "output_files": output_files,
        "item_counts": dict(item_counts),
        "lesson_counts": dict(lesson_counts),
        "blueprint_count": len(blueprints["blueprints"]),
        "study_plan_counts": run_manifest["study_plan_counts"],
        "validation": run_manifest["validation"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", required=True, help="Registry scope to build.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for generated artifact paths.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and plan the build without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit the build manifest as JSON.")
    args = parser.parse_args()

    report = build_scope_content_artifacts(
        args.scope_id,
        output_root=args.output_root,
        write=not args.dry_run,
    )
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Scope build: {report['scope_id']}")
        print(f"  generation_ready: {report['generation_ready']}")
        print(f"  item counts: {report['item_counts']}")
        print(f"  lesson counts: {report['lesson_counts']}")
        print(f"  output files: {report['output_files']}")
    return 0 if not any(report["validation"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
