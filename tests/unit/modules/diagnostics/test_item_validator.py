"""
Unit Tests — ItemValidator (P2-09)
====================================
Verifies that every one of the 8 validation rules correctly catches its
specific failure mode and that a fully-valid item passes all rules.

Run with: pytest tests/unit/modules/diagnostics/test_item_validator.py -v
"""

from __future__ import annotations

import uuid
from copy import deepcopy

import pytest

from app.domain.item_schema import ItemCreate, ItemType, ReviewStatus
from app.modules.diagnostics.item_validator import (
    ItemValidationError,
    ItemValidator,
    ValidationReport,
    flesch_kincaid_grade,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TOPIC_MAP = {
    "4.M.1.1": {
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Whole Numbers",
        "subtopic": "Count and Order 4-digit Numbers",
        "skill": "place_value_ordering",
    },
    "4.M.1.2": {
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Common Fractions",
        "subtopic": "Name and Compare Fractions",
        "skill": "fraction_comparison",
    },
}


def _valid_item(**overrides) -> ItemCreate:
    """Factory that returns a fully-valid MCQ ItemCreate."""
    base = {
        "item_id": uuid.uuid4(),
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Whole Numbers",
        "subtopic": "Count and Order",
        "skill": "place_value_ordering",
        "stem": "Thabo has 1 245 marbles. Sipho has 1 524 marbles. Who has more?",
        "answer_key": "B",
        "options": [
            {"label": "A", "text": "Thabo, because 1 245 is bigger"},
            {"label": "B", "text": "Sipho, because 1 524 is bigger"},
            {"label": "C", "text": "They have the same"},
            {"label": "D", "text": "We cannot tell without adding"},
        ],
        "explanation": (
            "To compare two 4-digit numbers, look at the thousands digit first. "
            "Both numbers have 1 thousand. Then look at the hundreds: 5 > 2, so 1 524 > 1 245. "
            "Sipho has more marbles."
        ),
        "distractor_rationale": {
            "A": "Learner compared digits right-to-left, confusing the units with the thousands.",
            "C": "Learner matched only the thousands digit and assumed equality.",
            "D": "Learner confused comparison with addition.",
        },
        "misconception_tags": ["place_value_confusion", "right_to_left_comparison"],
        "item_type": ItemType.MCQ,
        "difficulty_b": -0.5,
        "discrimination_a": 1.2,
        "guessing_c": 0.25,
        "language": "en",
        "review_status": ReviewStatus.AI_GENERATED,
        "source": "llm_generated",
        "safety_passed": True,
        "exposure_count": 0,
        "max_exposure": 50,
    }
    base.update(overrides)
    return ItemCreate.model_construct(**base)


@pytest.fixture
def validator() -> ItemValidator:
    return ItemValidator(topic_map=TOPIC_MAP)


# ---------------------------------------------------------------------------
# Rule 1 — CAPS reference exists
# ---------------------------------------------------------------------------


def test_rule1_valid_caps_ref(validator):
    item = _valid_item(caps_ref="4.M.1.1")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "caps_ref_exists")
    assert rule.passed


def test_rule1_unknown_caps_ref(validator):
    item = _valid_item(caps_ref="9.Z.9.9")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "caps_ref_exists")
    assert not rule.passed
    assert "9.Z.9.9" in rule.message


# ---------------------------------------------------------------------------
# Rule 2 — answer_key matches an option label
# ---------------------------------------------------------------------------


def test_rule2_valid_answer_key(validator):
    item = _valid_item(answer_key="B")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "answer_key_matches_option")
    assert rule.passed


def test_rule2_answer_key_not_in_options(validator):
    item = _valid_item(answer_key="E")  # no E option
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "answer_key_matches_option")
    assert not rule.passed
    assert "E" in rule.message


def test_rule2_skipped_for_non_mcq(validator):
    item = _valid_item(item_type=ItemType.SHORT_ANSWER, options=None)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "answer_key_matches_option")
    assert rule.passed  # skipped


# ---------------------------------------------------------------------------
# Rule 3 — stem readability (Flesch-Kincaid ≤ Grade 6)
# ---------------------------------------------------------------------------


def test_rule3_readable_stem(validator):
    item = _valid_item(stem="Thabo has 1 245 marbles. Sipho has 1 524 marbles. Who has more?")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "stem_readability")
    assert rule.passed


def test_rule3_complex_stem_fails(validator):
    complex_stem = (
        "Considering the multidimensional ramifications of hierarchical "
        "place-value decomposition methodologies in contemporary Grade 4 "
        "mathematical pedagogical frameworks, evaluate the comparative "
        "quantitative magnitudes of the following numerical representations."
    )
    item = _valid_item(stem=complex_stem)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "stem_readability")
    assert not rule.passed


def test_flesch_kincaid_grade_simple():
    grade = flesch_kincaid_grade("The cat sat on the mat. It was a big cat.")
    assert grade < 4.0


def test_flesch_kincaid_grade_academic():
    text = (
        "Polysyllabic lexicographic constructions substantially elevate "
        "the computational complexity of comprehension."
    )
    grade = flesch_kincaid_grade(text)
    assert grade > 6.0


# ---------------------------------------------------------------------------
# Rule 4 — No PII or harmful content
# ---------------------------------------------------------------------------


def test_rule4_clean_item_passes(validator):
    item = _valid_item()
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "no_pii_or_harmful")
    assert rule.passed


def test_rule4_sa_id_number_in_stem(validator):
    item = _valid_item(stem="Learner 9001015800084 scored 85 out of 100.")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "no_pii_or_harmful")
    assert not rule.passed
    assert "PII" in rule.message


def test_rule4_email_in_explanation(validator):
    item = _valid_item(explanation="Email teacher@school.co.za for help. " * 3)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "no_pii_or_harmful")
    assert not rule.passed


def test_rule4_harmful_word_in_stem(validator):
    item = _valid_item(stem="If you kill 3 animals and have 2 left, how many did you start with?")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "no_pii_or_harmful")
    assert not rule.passed


# ---------------------------------------------------------------------------
# Rule 5 — IRT parameters in bounds
# ---------------------------------------------------------------------------


def test_rule5_valid_irt_params(validator):
    item = _valid_item(difficulty_b=0.5, discrimination_a=1.2, guessing_c=0.25)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "irt_params_in_bounds")
    assert rule.passed


def test_rule5_discrimination_too_low(validator):
    item = _valid_item(discrimination_a=0.1)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "irt_params_in_bounds")
    assert not rule.passed
    assert "discrimination_a" in rule.message


def test_rule5_difficulty_out_of_range(validator):
    item = _valid_item(difficulty_b=5.0)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "irt_params_in_bounds")
    assert not rule.passed
    assert "difficulty_b" in rule.message


def test_rule5_guessing_too_high(validator):
    item = _valid_item(guessing_c=0.5)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "irt_params_in_bounds")
    assert not rule.passed
    assert "guessing_c" in rule.message


def test_rule5_multiple_irt_errors_reported(validator):
    item = _valid_item(discrimination_a=0.1, difficulty_b=10.0, guessing_c=0.9)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "irt_params_in_bounds")
    assert not rule.passed
    # All three errors should be in the message
    assert "discrimination_a" in rule.message
    assert "difficulty_b" in rule.message
    assert "guessing_c" in rule.message


# ---------------------------------------------------------------------------
# Rule 6 — Minimum 4 MCQ options
# ---------------------------------------------------------------------------


def test_rule6_four_options_pass(validator):
    item = _valid_item()
    assert len(item.options) == 4
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "minimum_mcq_options")
    assert rule.passed


def test_rule6_three_options_fail(validator):
    item = _valid_item(
        options=[
            {"label": "A", "text": "Option A"},
            {"label": "B", "text": "Option B"},
            {"label": "C", "text": "Option C"},
        ]
    )
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "minimum_mcq_options")
    assert not rule.passed
    assert "3" in rule.message


def test_rule6_skipped_for_short_answer(validator):
    item = _valid_item(item_type=ItemType.SHORT_ANSWER, options=None)
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "minimum_mcq_options")
    assert rule.passed


# ---------------------------------------------------------------------------
# Rule 7 — Explanation non-empty (≥ 40 chars)
# ---------------------------------------------------------------------------


def test_rule7_long_explanation_passes(validator):
    item = _valid_item(explanation="This is a detailed explanation that is definitely long enough for our purposes.")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "explanation_non_empty")
    assert rule.passed


def test_rule7_empty_explanation_fails(validator):
    item = _valid_item(explanation="")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "explanation_non_empty")
    assert not rule.passed


def test_rule7_short_explanation_fails(validator):
    item = _valid_item(explanation="Too short.")
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "explanation_non_empty")
    assert not rule.passed


# ---------------------------------------------------------------------------
# Rule 8 — Distractor rationale covers all wrong options
# ---------------------------------------------------------------------------


def test_rule8_all_distractors_covered(validator):
    item = _valid_item()  # B is correct; A, C, D covered in distractor_rationale
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "distractor_rationale_complete")
    assert rule.passed


def test_rule8_missing_distractor_fails(validator):
    item = _valid_item(
        distractor_rationale={
            "A": "Misconception A",
            # "C" missing
            "D": "Misconception D",
        }
    )
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "distractor_rationale_complete")
    assert not rule.passed
    assert "C" in rule.message


def test_rule8_skipped_for_true_false(validator):
    item = _valid_item(
        item_type=ItemType.TRUE_FALSE,
        options=None,
        distractor_rationale=None,
    )
    report = validator.validate(item)
    rule = next(r for r in report.rules if r.rule == "distractor_rationale_complete")
    assert rule.passed


# ---------------------------------------------------------------------------
# Integration — fully valid item passes all 8 rules
# ---------------------------------------------------------------------------


def test_all_rules_pass_for_valid_item(validator):
    item = _valid_item()
    report = validator.validate(item)
    assert report.passed, f"Expected all rules to pass. Failures: {report.failures}"
    assert len(report.rules) == 8


def test_validation_report_as_dict(validator):
    item = _valid_item()
    report = validator.validate(item)
    d = report.as_dict()
    assert "item_id" in d
    assert "passed" in d
    assert "rules" in d
    assert isinstance(d["rules"], list)
    assert len(d["rules"]) == 8


def test_item_validation_error_message(validator):
    item = _valid_item(caps_ref="INVALID.REF", answer_key="Z")
    report = validator.validate(item)
    assert not report.passed
    with pytest.raises(ItemValidationError) as exc_info:
        if not report.passed:
            raise ItemValidationError(report)
    assert "caps_ref_exists" in str(exc_info.value)
