"""
Item Generator — P2-03
========================
LLM-powered diagnostic item generation pipeline.

Flow per item:
  1. Build Jinja2 prompt from caps_ref + difficulty_target
  2. Call primary LLM gateway (Groq first, Anthropic fallback)
  3. Parse structured JSON response into ItemCreate
  4. Run ItemValidator (8 rules)
  5. Run independent answer-key verification call (P2-07 pattern)
  6. Return validated ItemCreate or raise ItemGenerationError

Two-call verification (§6.2 / P2-07 mandate):
  A *separate* LLM call re-solves the question from scratch without seeing
  the original answer_key.  If both calls agree → item passes.
  If they disagree → item is flagged with review_status=ai_generated for
  mandatory human review rather than being silently rejected.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.domain.item_schema import ItemCreate, ItemType, ReviewStatus
from app.modules.diagnostics.item_validator import (
    ItemValidationError,
    ItemValidator,
    ValidationReport,
)

logger = logging.getLogger(__name__)

# Template directory relative to this module's package root
_PROMPTS_DIR = Path(__file__).parent / "prompts"


class DifficultyBand(str, Enum):
    EASY = "easy"           # b < -1.0
    MODERATE = "moderate"   # -1.0 ≤ b < 0.0
    ON_LEVEL = "on_level"   # 0.0 ≤ b < 1.0
    CHALLENGING = "challenging"  # b ≥ 1.0


# IRT b-param target ranges per difficulty band
DIFFICULTY_BAND_RANGES: dict[DifficultyBand, tuple[float, float]] = {
    DifficultyBand.EASY: (-2.5, -1.0),
    DifficultyBand.MODERATE: (-1.0, 0.0),
    DifficultyBand.ON_LEVEL: (0.0, 1.0),
    DifficultyBand.CHALLENGING: (1.0, 2.5),
}


@dataclass
class ItemGenerationResult:
    item: ItemCreate
    validation_report: ValidationReport
    answer_key_verified: bool
    answer_key_agreement: bool  # True = LLM 1 & LLM 2 agree
    generation_attempts: int


class ItemGenerationError(Exception):
    """Raised when item generation fails after exhausting retries."""

    def __init__(self, caps_ref: str, reason: str, attempts: int) -> None:
        self.caps_ref = caps_ref
        self.reason = reason
        self.attempts = attempts
        super().__init__(
            f"ItemGenerationError for {caps_ref} after {attempts} attempt(s): {reason}"
        )


class ItemGenerator:
    """
    Generates CAPS-aligned diagnostic items for a given topic reference.

    Args:
        llm_gateway:    Production gateway instance (Groq/Anthropic).
        validator:      ItemValidator loaded with the CAPS topic map.
        topic_map:      dict mapping caps_ref → topic metadata.
        max_retries:    Per-item generation retries on validation failure.
    """

    def __init__(
        self,
        llm_gateway: Any,
        validator: ItemValidator,
        topic_map: dict[str, Any],
        *,
        max_retries: int = 3,
    ) -> None:
        self._gateway = llm_gateway
        self._validator = validator
        self._topic_map = topic_map
        self._max_retries = max_retries
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(_PROMPTS_DIR)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(
        self,
        caps_ref: str,
        difficulty_band: DifficultyBand,
        *,
        language: str = "en",
        item_type: ItemType = ItemType.MCQ,
    ) -> ItemGenerationResult:
        """
        Generate, validate, and verify one diagnostic item.

        Returns an ItemGenerationResult on success.
        Raises ItemGenerationError if all retries are exhausted.
        """
        if caps_ref not in self._topic_map:
            raise ItemGenerationError(
                caps_ref,
                f"caps_ref not in topic map — cannot generate",
                attempts=0,
            )

        topic_meta = self._topic_map[caps_ref]
        b_min, b_max = DIFFICULTY_BAND_RANGES[difficulty_band]
        b_target = (b_min + b_max) / 2

        last_error: str = "unknown"
        for attempt in range(1, self._max_retries + 1):
            logger.info(
                "Generating item caps_ref=%s band=%s attempt=%d/%d",
                caps_ref, difficulty_band.value, attempt, self._max_retries,
            )
            try:
                raw_json = await self._call_generation_llm(
                    caps_ref=caps_ref,
                    topic_meta=topic_meta,
                    difficulty_band=difficulty_band,
                    b_target=b_target,
                    language=language,
                    item_type=item_type,
                )
                item = self._parse_item(raw_json, caps_ref, language)

                # Validation gate (8 rules)
                report = self._validator.validate(item)
                if not report.passed:
                    last_error = "; ".join(
                        f"[{r.rule}] {r.message}" for r in report.failures
                    )
                    logger.warning("Item failed validation attempt %d: %s", attempt, last_error)
                    continue

                # Answer-key verification (mandatory 2nd LLM call)
                verified, agreed = await self._verify_answer_key(item)

                if not agreed:
                    # Mark for human review but still return to allow
                    # the caller to decide (generate_items.py may skip)
                    item.review_status = ReviewStatus.AI_GENERATED
                    logger.warning(
                        "Answer-key disagreement for item %s — flagged for human review",
                        item.item_id,
                    )
                else:
                    item.review_status = ReviewStatus.AI_GENERATED

                return ItemGenerationResult(
                    item=item,
                    validation_report=report,
                    answer_key_verified=verified,
                    answer_key_agreement=agreed,
                    generation_attempts=attempt,
                )

            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                last_error = f"Parse error: {exc}"
                logger.warning("Generation attempt %d parse error: %s", attempt, exc)
                continue

        raise ItemGenerationError(caps_ref, last_error, attempts=self._max_retries)

    async def generate_batch(
        self,
        caps_ref: str,
        n_items: int,
        difficulty_band: DifficultyBand,
        *,
        language: str = "en",
        item_type: ItemType = ItemType.MCQ,
    ) -> list[ItemGenerationResult]:
        """
        Generate *n_items* candidates for a CAPS ref.  Failed items are skipped
        and logged.  Returns whatever succeeded (may be < n_items).
        """
        results: list[ItemGenerationResult] = []
        for i in range(n_items):
            try:
                result = await self.generate(
                    caps_ref, difficulty_band, language=language, item_type=item_type
                )
                results.append(result)
                logger.info(
                    "Generated item %d/%d for %s [agreed=%s]",
                    i + 1, n_items, caps_ref, result.answer_key_agreement,
                )
            except ItemGenerationError as exc:
                logger.error("Failed to generate item %d/%d: %s", i + 1, n_items, exc)

        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _call_generation_llm(
        self,
        caps_ref: str,
        topic_meta: dict,
        difficulty_band: DifficultyBand,
        b_target: float,
        language: str,
        item_type: ItemType,
    ) -> dict:
        """Render the generation prompt and call the LLM gateway."""
        template = self._jinja_env.get_template("item_generation_v1.jinja2")
        prompt = template.render(
            caps_ref=caps_ref,
            grade=topic_meta.get("grade", 4),
            subject=topic_meta.get("subject", "Mathematics"),
            term=topic_meta.get("term", 1),
            topic=topic_meta.get("topic", ""),
            subtopic=topic_meta.get("subtopic", ""),
            skill=topic_meta.get("skill", ""),
            difficulty_band=difficulty_band.value,
            b_target=round(b_target, 2),
            language=language,
            item_type=item_type.value,
        )

        response_text = await self._gateway.complete(
            prompt=prompt,
            max_tokens=1800,
            temperature=0.7,
            response_format="json",
        )
        return json.loads(response_text)

    def _parse_item(self, raw: dict, caps_ref: str, language: str) -> ItemCreate:
        """
        Map raw LLM JSON to an ItemCreate Pydantic model.
        Assigns a fresh UUID if the LLM omitted item_id.
        """
        raw.setdefault("item_id", str(uuid.uuid4()))
        raw.setdefault("caps_ref", caps_ref)
        raw.setdefault("language", language)
        raw.setdefault("review_status", ReviewStatus.AI_GENERATED.value)
        raw.setdefault("source", "llm_generated")
        raw.setdefault("safety_passed", False)  # set True only after verification
        raw.setdefault("exposure_count", 0)
        raw.setdefault("max_exposure", 50)
        raw.setdefault("discrimination_a", 1.0)
        raw.setdefault("guessing_c", 0.25)
        return ItemCreate(**raw)

    async def _verify_answer_key(
        self, item: ItemCreate
    ) -> tuple[bool, bool]:
        """
        Independent 2nd LLM call (P2-07) that re-solves the question without
        seeing the original answer_key.

        Returns:
            (verified: bool, agreed: bool)
            ``verified`` — the call completed without error.
            ``agreed``   — the independent answer matches item.answer_key.
        """
        template = self._jinja_env.get_template("answer_key_verification_v1.jinja2")
        prompt = template.render(
            stem=item.stem,
            options=item.options or [],
            explanation=item.explanation,
            caps_ref=item.caps_ref,
        )

        try:
            response_text = await self._gateway.complete(
                prompt=prompt,
                max_tokens=400,
                temperature=0.0,  # deterministic for verification
                response_format="json",
            )
            result = json.loads(response_text)
            independent_answer = str(result.get("answer", "")).strip().upper()
            agreed = independent_answer == str(item.answer_key).strip().upper()

            if agreed:
                item.safety_passed = True  # both calls agree → mark safe

            logger.info(
                "Answer-key verification item=%s original=%s independent=%s agreed=%s",
                item.item_id, item.answer_key, independent_answer, agreed,
            )
            return True, agreed

        except Exception as exc:  # noqa: BLE001
            logger.error("Answer-key verification failed for item %s: %s", item.item_id, exc)
            return False, False
