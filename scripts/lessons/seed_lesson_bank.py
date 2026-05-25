#!/usr/bin/env python3
"""Seed approved lesson-bank artifacts into the lessons table for a learner."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import AsyncSessionLocal
from app.models import Lesson
from app.modules.lessons.lesson_validator import LessonValidator

DEFAULT_INPUT = ROOT / "data" / "generated" / "lessons" / "grade4_maths_launch_lessons.json"


def lesson_row(lesson: dict, learner_id: str) -> dict:
    return {
        "id": lesson.get("lesson_id"),
        "learner_id": learner_id,
        "grade": lesson["grade"],
        "subject": lesson["subject"],
        "topic": lesson["topic"],
        "content": json.dumps(lesson),
        "caps_ref": lesson["caps_ref"],
        "caps_reference": lesson["caps_ref"],
        "term": lesson.get("term"),
        "subtopic": lesson.get("subtopic"),
        "learning_objectives": lesson.get("learning_objectives", []),
        "explanation": lesson.get("explanation"),
        "worked_examples": lesson.get("worked_examples", []),
        "practice_questions": lesson.get("practice_questions", []),
        "answer_key": lesson.get("answer_key", []),
        "remediation_hints": lesson.get("remediation_hints", []),
        "difficulty_level": lesson.get("difficulty_level"),
        "language_level": lesson.get("language_level"),
        "safety_classification": lesson.get("safety_classification", "safe"),
        "pii_check_passed": bool(lesson.get("pii_check_passed")),
        "answer_key_verified": bool(lesson.get("answer_key_verified")),
        "quality_score": float(lesson.get("quality_score") or 0.0),
        "trust_label": lesson.get("trust_label", {}),
        "review_status": lesson.get("review_status", "approved"),
        "reviewer_id": UUID(lesson["reviewer_id"]) if lesson.get("reviewer_id") else None,
        "prompt_template_version": lesson.get("prompt_template_version"),
        "provider": lesson.get("provider"),
        "model_version": lesson.get("model_version"),
        "generation_latency_ms": int(lesson.get("generation_latency_ms") or 0),
        "token_usage": lesson.get("token_usage", {}),
        "variant_type": lesson.get("variant_type", "standard"),
        "llm_provider": lesson.get("provider", "google"),
    }


async def seed(args: argparse.Namespace) -> int:
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    lessons = payload.get("lessons", [])
    validator = LessonValidator()
    for lesson in lessons:
        result = validator.validate(lesson, require_verified=True)
        if not result.passed:
            raise SystemExit(f"Lesson {lesson.get('lesson_id')} failed validation: {result.failures}")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "lessons": len(lessons)}, indent=2))
        return 0
    if not args.learner_id:
        raise SystemExit("--learner-id is required unless --dry-run is used")
    async with AsyncSessionLocal() as session:
        for lesson in lessons:
            row = lesson_row(lesson, args.learner_id)
            existing = await session.get(Lesson, row["id"])
            if existing:
                for key, value in row.items():
                    setattr(existing, key, value)
            else:
                session.add(Lesson(**row))
        await session.commit()
    print(json.dumps({"seeded": len(lessons), "learner_id": args.learner_id}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--learner-id")
    parser.add_argument("--dry-run", action="store_true")
    return asyncio.run(seed(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
