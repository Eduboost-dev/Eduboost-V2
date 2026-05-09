"""
Item Validator — P2-02
========================
Eight-rule validation gate for every diagnostic item before it enters the
item bank.  All rules are independent and synchronous except ``safety_llm_pass``
which makes a single async LLM call when ``use_llm_safety=True``.

Usage (sync):
    from app.modules.diagnostics.item_validator import ItemValidator
    validator = ItemValidator(topic_map=caps_topic_map)
    report = validator.validate(item_create)
    if not report.passed:
        raise ItemValidationError(report)

Usage (async, with LLM safety):
    report = await validator.validate_async(item_create)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.domain.item_schema import ItemCreate, ItemType


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class RuleResult:
    rule: str
    passed: bool
    message: str


@dataclass
class ValidationReport:
    item_id: str
    rules: list[RuleResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.rules)

    @property
    def failures(self) -> list[RuleResult]:
        return [r for r in self.rules if not r.passed]

    def as_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "passed": self.passed,
            "rules": [
                {"rule": r.rule, "passed": r.passed, "message": r.message}
                for r in self.rules
            ],
        }


class ItemValidationError(Exception):
    """Raised when an item fails one or more validation rules."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        failures = "; ".join(f"[{r.rule}] {r.message}" for r in report.failures)
        super().__init__(f"Item {report.item_id} failed validation: {failures}")


# ---------------------------------------------------------------------------
# PII / harmful-content patterns (Rule 4 — regex tier)
# ---------------------------------------------------------------------------

_PII_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b\d{13}\b"),                        # SA ID number
    re.compile(r"\b\d{10,}\b"),                       # phone-length digit strings
    re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),  # email
    re.compile(r"\b(?:27|0)[6-8]\d{8}\b"),            # SA mobile number
    re.compile(r"http[s]?://\S+"),                     # raw URLs
]

_HARMFUL_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(kill|murder|rape|abuse|weapon|bomb|drug|sex)\b", re.IGNORECASE),
    re.compile(r"\b(alcohol|cigarette|smoking|gambling)\b", re.IGNORECASE),
]

# IRT parameter bounds
_IRT_A_MIN, _IRT_A_MAX = 0.5, 2.5
_IRT_B_MIN, _IRT_B_MAX = -3.0, 3.0
_IRT_C_MIN, _IRT_C_MAX = 0.0, 0.35

# Flesch-Kincaid approximate Grade 6 ceiling (≈ FK Grade 6.0 → score ≈ 70)
_FK_GRADE_CEILING = 6.0


# ---------------------------------------------------------------------------
# Readability helpers (approximated Flesch-Kincaid Grade Level)
# ---------------------------------------------------------------------------


def _count_syllables(word: str) -> int:
    """Rough syllable counter sufficient for FK-GL approximation."""
    word = word.lower().strip(".,!?;:'\"()[]")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent-e correction
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_kincaid_grade(text: str) -> float:
    """
    Approximate Flesch-Kincaid Grade Level.
    FK-GL = 0.39 × (words/sentences) + 11.8 × (syllables/words) − 15.59
    Returns 0.0 for empty / single-word inputs (no sentences parseable).
    """
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = text.split()
    if not sentences or not words:
        return 0.0

    syllables = sum(_count_syllables(w) for w in words)
    avg_sentence_len = len(words) / len(sentences)
    avg_syllables = syllables / len(words)
    return 0.39 * avg_sentence_len + 11.8 * avg_syllables - 15.59


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------


class ItemValidator:
    """
    Stateless validator — thread-safe and reusable across items.

    Args:
        topic_map: dict mapping caps_ref strings to their topic metadata,
                   as loaded from ``data/caps/caps_topic_map_grade4_maths.json``.
        use_llm_safety: when True, ``validate_async`` makes a second LLM call
                        (P2-07 pattern) for the safety check; the sync
                        ``validate`` method only runs regex-tier safety.
    """

    def __init__(
        self,
        topic_map: dict[str, Any],
        *,
        use_llm_safety: bool = False,
    ) -> None:
        self._topic_map = topic_map
        self._use_llm_safety = use_llm_safety

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, item: ItemCreate) -> ValidationReport:
        """Run all eight rules synchronously (no LLM safety call)."""
        report = ValidationReport(item_id=str(item.item_id))
        report.rules = [
            self._rule_caps_ref_exists(item),
            self._rule_answer_key_matches_option(item),
            self._rule_stem_readability(item),
            self._rule_no_pii_or_harmful(item),
            self._rule_irt_params_in_bounds(item),
            self._rule_minimum_mcq_options(item),
            self._rule_explanation_non_empty(item),
            self._rule_distractor_rationale_complete(item),
        ]
        return report

    async def validate_async(
        self,
        item: ItemCreate,
        *,
        llm_gateway: Any | None = None,
    ) -> ValidationReport:
        """
        Run all eight rules; optionally replaces regex safety with an LLM
        safety call when ``use_llm_safety=True`` and a gateway is supplied.
        """
        report = self.validate(item)

        if self._use_llm_safety and llm_gateway is not None:
            # Replace the regex safety result with the LLM result
            llm_result = await self._rule_llm_safety(item, llm_gateway)
            report.rules = [
                r for r in report.rules if r.rule != "no_pii_or_harmful"
            ]
            report.rules.insert(3, llm_result)

        return report

    # ------------------------------------------------------------------
    # Rule 1 — CAPS reference exists in topic map
    # ------------------------------------------------------------------

    def _rule_caps_ref_exists(self, item: ItemCreate) -> RuleResult:
        rule = "caps_ref_exists"
        if item.caps_ref in self._topic_map:
            return RuleResult(rule=rule, passed=True, message="caps_ref found in topic map")
        return RuleResult(
            rule=rule,
            passed=False,
            message=(
                f"caps_ref '{item.caps_ref}' not found in topic map. "
                f"Known refs: {list(self._topic_map.keys())[:10]} …"
            ),
        )

    # ------------------------------------------------------------------
    # Rule 2 — answer_key matches one of options[].label
    # ------------------------------------------------------------------

    def _rule_answer_key_matches_option(self, item: ItemCreate) -> RuleResult:
        rule = "answer_key_matches_option"
        if not item.options:
            return RuleResult(rule=rule, passed=True, message="No options (non-MCQ item — skipped)")

        option_labels = {opt.get("label", "") for opt in item.options}
        if item.answer_key in option_labels:
            return RuleResult(rule=rule, passed=True, message=f"answer_key '{item.answer_key}' is valid")
        return RuleResult(
            rule=rule,
            passed=False,
            message=(
                f"answer_key '{item.answer_key}' not in option labels "
                f"{sorted(option_labels)}"
            ),
        )

    # ------------------------------------------------------------------
    # Rule 3 — stem readability ≤ Grade 6 Flesch-Kincaid
    # ------------------------------------------------------------------

    def _rule_stem_readability(self, item: ItemCreate) -> RuleResult:
        rule = "stem_readability"
        grade = flesch_kincaid_grade(item.stem)
        if grade <= _FK_GRADE_CEILING:
            return RuleResult(
                rule=rule,
                passed=True,
                message=f"FK Grade Level {grade:.2f} ≤ {_FK_GRADE_CEILING}",
            )
        return RuleResult(
            rule=rule,
            passed=False,
            message=(
                f"FK Grade Level {grade:.2f} exceeds ceiling {_FK_GRADE_CEILING}. "
                "Simplify the question stem for Grade 4 reading level."
            ),
        )

    # ------------------------------------------------------------------
    # Rule 4 — No PII or harmful content (regex tier)
    # ------------------------------------------------------------------

    def _rule_no_pii_or_harmful(self, item: ItemCreate) -> RuleResult:
        rule = "no_pii_or_harmful"
        corpus = " ".join(
            filter(
                None,
                [
                    item.stem,
                    item.explanation,
                    *(opt.get("text", "") for opt in (item.options or [])),
                    *(item.distractor_rationale.values() if item.distractor_rationale else []),
                ],
            )
        )
        for pattern in _PII_PATTERNS:
            match = pattern.search(corpus)
            if match:
                return RuleResult(
                    rule=rule,
                    passed=False,
                    message=f"Potential PII detected: '{match.group()[:30]}…'",
                )
        for pattern in _HARMFUL_PATTERNS:
            match = pattern.search(corpus)
            if match:
                return RuleResult(
                    rule=rule,
                    passed=False,
                    message=f"Potentially harmful content detected: '{match.group()}'",
                )
        return RuleResult(rule=rule, passed=True, message="No PII or harmful content detected (regex)")

    async def _rule_llm_safety(self, item: ItemCreate, llm_gateway: Any) -> RuleResult:
        """
        LLM-based safety pass — called only in validate_async when enabled.
        Delegates to the production LLM gateway's safety endpoint.
        Returns a RuleResult with the LLM verdict.
        """
        rule = "no_pii_or_harmful"
        try:
            result = await llm_gateway.safety_check(
                text=item.stem + " " + item.explanation,
                context="diagnostic_item",
            )
            if result.safe:
                return RuleResult(rule=rule, passed=True, message="LLM safety check passed")
            return RuleResult(
                rule=rule,
                passed=False,
                message=f"LLM safety check failed: {result.reason}",
            )
        except Exception as exc:  # noqa: BLE001
            # Fail-safe: treat LLM error as failure to force human review
            return RuleResult(
                rule=rule,
                passed=False,
                message=f"LLM safety call error (fail-safe): {exc}",
            )

    # ------------------------------------------------------------------
    # Rule 5 — IRT parameters within valid bounds
    # ------------------------------------------------------------------

    def _rule_irt_params_in_bounds(self, item: ItemCreate) -> RuleResult:
        rule = "irt_params_in_bounds"
        errors: list[str] = []
        if not (_IRT_A_MIN <= item.discrimination_a <= _IRT_A_MAX):
            errors.append(
                f"discrimination_a={item.discrimination_a} not in [{_IRT_A_MIN}, {_IRT_A_MAX}]"
            )
        if not (_IRT_B_MIN <= item.difficulty_b <= _IRT_B_MAX):
            errors.append(
                f"difficulty_b={item.difficulty_b} not in [{_IRT_B_MIN}, {_IRT_B_MAX}]"
            )
        if not (_IRT_C_MIN <= item.guessing_c <= _IRT_C_MAX):
            errors.append(
                f"guessing_c={item.guessing_c} not in [{_IRT_C_MIN}, {_IRT_C_MAX}]"
            )
        if errors:
            return RuleResult(rule=rule, passed=False, message="; ".join(errors))
        return RuleResult(rule=rule, passed=True, message="All IRT parameters within valid bounds")

    # ------------------------------------------------------------------
    # Rule 6 — At least 4 MCQ options
    # ------------------------------------------------------------------

    def _rule_minimum_mcq_options(self, item: ItemCreate) -> RuleResult:
        rule = "minimum_mcq_options"
        if item.item_type != ItemType.MCQ:
            return RuleResult(rule=rule, passed=True, message=f"item_type={item.item_type} — MCQ check skipped")
        n = len(item.options or [])
        if n >= 4:
            return RuleResult(rule=rule, passed=True, message=f"{n} MCQ options provided")
        return RuleResult(
            rule=rule,
            passed=False,
            message=f"MCQ requires ≥ 4 options; only {n} provided",
        )

    # ------------------------------------------------------------------
    # Rule 7 — explanation non-empty and minimum length
    # ------------------------------------------------------------------

    def _rule_explanation_non_empty(self, item: ItemCreate) -> RuleResult:
        rule = "explanation_non_empty"
        MIN_CHARS = 40  # roughly one meaningful sentence
        explanation = (item.explanation or "").strip()
        if len(explanation) >= MIN_CHARS:
            return RuleResult(
                rule=rule,
                passed=True,
                message=f"Explanation present ({len(explanation)} chars)",
            )
        return RuleResult(
            rule=rule,
            passed=False,
            message=(
                f"Explanation too short: {len(explanation)} chars < {MIN_CHARS}. "
                "Must explain why the correct answer is correct in learner-accessible language."
            ),
        )

    # ------------------------------------------------------------------
    # Rule 8 — distractor_rationale covers all wrong options
    # ------------------------------------------------------------------

    def _rule_distractor_rationale_complete(self, item: ItemCreate) -> RuleResult:
        rule = "distractor_rationale_complete"
        if item.item_type != ItemType.MCQ or not item.options:
            return RuleResult(rule=rule, passed=True, message="Non-MCQ item — distractor check skipped")

        wrong_labels = {
            opt["label"] for opt in item.options if opt.get("label") != item.answer_key
        }
        rationale_keys = set(item.distractor_rationale.keys() if item.distractor_rationale else [])

        missing = wrong_labels - rationale_keys
        if not missing:
            return RuleResult(
                rule=rule,
                passed=True,
                message=f"Distractor rationale covers all {len(wrong_labels)} wrong options",
            )
        return RuleResult(
            rule=rule,
            passed=False,
            message=(
                f"Missing distractor rationale for options: {sorted(missing)}. "
                "Every wrong answer must map to a documented misconception."
            ),
        )
