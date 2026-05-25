from __future__ import annotations

from app.services.content_generation.lesson_generator import LessonGenerator
from app.services.content_generation.prompt_payloads import GeneratedLesson


def _lesson(**kwargs):
    data = {
        "title": "Lesson",
        "summary": "Summary",
        "learning_objectives": ["Objective"],
        "teacher_notes": "Notes",
        "learner_activity": "Activity",
        "worked_examples": ["Example"],
        "practice_questions": ["Question"],
        "answer_key": ["Answer"],
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "MAT",
        "language": "en",
        "source_chunk_ids": ["chunk-1"],
    }
    data.update(kwargs)
    return GeneratedLesson(**data)


def test_lesson_generator_accepts_schema_valid_lesson() -> None:
    assert LessonGenerator().validate(_lesson(), caps_ref="4.M.1.1") == []


def test_lesson_without_answer_key_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(answer_key=[]), caps_ref="4.M.1.1")

    assert any("answer key" in error for error in errors)


def test_lesson_without_objectives_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(learning_objectives=[]), caps_ref="4.M.1.1")

    assert any("objectives" in error for error in errors)
