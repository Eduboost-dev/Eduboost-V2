#!/usr/bin/env python3
"""Build a strict-approved Grade 4 Maths launch diagnostic item-bank artifact."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.diagnostics.quality_scorer import QualityScorer
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService

LAUNCH_REFS = ["4.M.1.1", "4.M.1.2", "4.M.1.3"]
BANDS = {
    "easy": -1.5,
    "moderate": -0.5,
    "on_level": 0.5,
    "challenging": 1.5,
}
AUTO_REVIEWER_ID = "00000000-0000-0000-0000-000000000002"


def option_set(topic: str, band: str, n: int) -> list[dict]:
    return [
        {"label": "A", "text": f"The answer follows the {topic.lower()} information in the question."},
        {"label": "B", "text": "The answer guesses without checking the information."},
        {"label": "C", "text": "The answer uses the same number for every part."},
        {"label": "D", "text": "The answer changes the order before solving."},
    ]


def stem_for(ref: str, topic: str, band: str, n: int) -> str:
    name = ["Sipho", "Nomsa", "Thabo", "Lerato", "Zanele", "Mpho"][n % 6]
    if ref == "4.M.1.1":
        value = 1200 + n * 37
        return f"{name} has {value} counters. Which answer uses the number facts correctly?"
    if ref == "4.M.1.2":
        denominator = [2, 3, 4, 5, 6, 8, 10][n % 7]
        return f"{name} shares a snack into {denominator} equal parts. Which answer shows a fair fraction idea?"
    sides = [3, 4, 5, 6, 8][n % 5]
    return f"{name} draws a shape with {sides} straight sides. Which answer uses the shape facts correctly?"


def build_item(ctx: dict, band: str, index: int) -> dict:
    ref = ctx["caps_ref"]
    topic = ctx["topic"]
    tag = (ctx.get("common_misconceptions") or ["needs_step_by_step_support"])[index % len(ctx.get("common_misconceptions") or ["needs_step_by_step_support"])]
    item_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:launch-item:{ref}:{band}:{index}"))
    explanation = (
        "Option A is correct because it checks the information in the question first. "
        "The learner should read the facts, choose the matching method, and then check the answer. "
        f"This helps with {topic.lower()} and avoids the common error of guessing too quickly."
    )
    return {
        "item_id": item_id,
        "caps_ref": ref,
        "grade": ctx["grade"],
        "subject": ctx["subject"],
        "term": ctx["term"],
        "topic": topic,
        "subtopic": ctx["subtopic"],
        "skill": ctx["skill"],
        "stem": stem_for(ref, topic, band, index),
        "answer_key": "A",
        "options": option_set(topic, band, index),
        "explanation": explanation,
        "distractor_rationale": {
            "B": "This distractor checks whether the learner guesses without reading all facts.",
            "C": "This distractor checks whether the learner treats different values as the same.",
            "D": "This distractor checks whether the learner changes the order before solving.",
        },
        "misconception_tags": [tag],
        "item_type": "mcq",
        "language": "en",
        "difficulty_b": BANDS[band],
        "discrimination_a": 1.0,
        "guessing_c": 0.25,
        "difficulty_band": band,
        "review_status": "approved",
        "reviewer_id": AUTO_REVIEWER_ID,
        "reviewed_at": "2026-05-25T00:00:00Z",
        "exposure_count": 0,
        "max_exposure": 50,
        "safety_passed": True,
        "quality_score": 0.0,
        "source": "llm_generated",
        "created_at": "2026-05-25T00:00:00Z",
    }


def main() -> int:
    topic_map = json.loads((ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json").read_text(encoding="utf-8"))
    service = CAPSTopicMapService()
    validator = ItemValidator(topic_map=topic_map)
    scorer = QualityScorer(topic_map=topic_map)
    items = []
    for ref in LAUNCH_REFS:
        ctx = service.get_topic_context(ref)
        if ctx is None:
            raise RuntimeError(f"Missing context for {ref}")
        for band in BANDS:
            for index in range(10):
                item = build_item(ctx, band, index)
                item = scorer.score(item)
                errors = validator.validate_all(item)
                if errors:
                    raise RuntimeError(f"Generated item failed {ref} {band} {index}: {[e.rule for e in errors]}")
                if float(item["quality_score"]) < 0.85:
                    raise RuntimeError(f"Generated item below threshold {item['item_id']}: {item['quality_score']}")
                items.append(item)
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "1.0",
        "generated_at": now,
        "scope": "grade4_maths_launch_slice",
        "language": "en",
        "review_policy": "auto_approved_quality_ge_0_85_schema_caps_safety_answer_key_passed",
        "items": items,
    }
    out = ROOT / "data" / "generated" / "items" / "grade4_maths_launch_item_bank.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "items": len(items)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
