#!/usr/bin/env python
"""
generate_items.py — P2-04
===========================
CLI to generate CAPS-aligned diagnostic items via the LLM gateway and write
validated items to the seed JSON file.

Usage:
    python scripts/generate_items.py \\
        --caps-ref 4.M.1.1 \\
        --n-items 60 \\
        --difficulty-band easy \\
        --output data/caps/grade4_maths_item_bank.json \\
        [--dry-run] \\
        [--require-agreement] \\
        [--language en]

Options:
    --caps-ref          CAPS reference code (e.g. 4.M.1.1)
    --n-items           Number of candidate items to generate (recommend 60 → ≥40 pass)
    --difficulty-band   easy | moderate | on_level | challenging
    --output            Path to the seed JSON file (items are appended)
    --dry-run           Generate and validate but do NOT write to the output file
    --require-agreement Only write items where answer-key verification agreed
    --language          Language code: en (default), zu, af, xh
    --topic-map         Path to CAPS topic map JSON (default: data/caps/caps_topic_map_grade4_maths.json)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path when run from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.llm_gateway import get_llm_gateway  # noqa: E402
from app.modules.diagnostics.item_generator import (  # noqa: E402
    DifficultyBand,
    ItemGenerationError,
    ItemGenerator,
)
from app.modules.diagnostics.item_validator import ItemValidator  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("generate_items")

DEFAULT_TOPIC_MAP = Path("data/caps/caps_topic_map_grade4_maths.json")
DEFAULT_OUTPUT = Path("data/caps/grade4_maths_item_bank.json")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate CAPS-aligned diagnostic items via LLM gateway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--caps-ref", required=True, help="CAPS reference code e.g. 4.M.1.1")
    parser.add_argument("--n-items", type=int, default=60, help="Number of candidates to generate")
    parser.add_argument(
        "--difficulty-band",
        choices=[b.value for b in DifficultyBand],
        default=DifficultyBand.ON_LEVEL.value,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate but do not write to output file",
    )
    parser.add_argument(
        "--require-agreement",
        action="store_true",
        help="Skip items where LLM answer-key verification disagreed",
    )
    parser.add_argument("--language", default="en", choices=["en", "zu", "af", "xh"])
    parser.add_argument("--topic-map", type=Path, default=DEFAULT_TOPIC_MAP)
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Seed file I/O
# ---------------------------------------------------------------------------


def load_seed_file(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Accept both a bare list and a wrapped {"items": [...]} envelope
    if isinstance(data, list):
        return data
    return data.get("items", [])


def save_seed_file(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "schema_version": "1.0",
                "generated_at": datetime.now(tz=timezone.utc).isoformat(),
                "item_count": len(items),
                "items": items,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


def item_to_dict(item_create) -> dict:
    """Convert Pydantic ItemCreate to a plain dict for JSON serialisation."""
    d = item_create.model_dump() if hasattr(item_create, "model_dump") else item_create.dict()
    # Ensure UUID fields are strings
    for key in ("item_id", "reviewer_id"):
        if key in d and d[key] is not None:
            d[key] = str(d[key])
    return d


# ---------------------------------------------------------------------------
# Main async entrypoint
# ---------------------------------------------------------------------------


async def main(args: argparse.Namespace) -> int:
    # Load CAPS topic map
    if not args.topic_map.exists():
        logger.error("Topic map not found: %s", args.topic_map)
        return 1

    with open(args.topic_map, encoding="utf-8") as f:
        topic_map = json.load(f)

    if args.caps_ref not in topic_map:
        logger.error("caps_ref '%s' not found in topic map %s", args.caps_ref, args.topic_map)
        return 1

    # Initialise services
    llm_gateway = get_llm_gateway()
    validator = ItemValidator(topic_map=topic_map)
    generator = ItemGenerator(
        llm_gateway=llm_gateway,
        validator=validator,
        topic_map=topic_map,
        max_retries=3,
    )

    difficulty_band = DifficultyBand(args.difficulty_band)
    logger.info(
        "Generating %d items | caps_ref=%s | band=%s | language=%s",
        args.n_items, args.caps_ref, difficulty_band.value, args.language,
    )

    # Generation loop
    passed: list[dict] = []
    failed = 0
    disagreed = 0

    results = await generator.generate_batch(
        caps_ref=args.caps_ref,
        n_items=args.n_items,
        difficulty_band=difficulty_band,
        language=args.language,
    )

    for result in results:
        if not result.validation_report.passed:
            failed += 1
            continue

        if args.require_agreement and not result.answer_key_agreement:
            disagreed += 1
            logger.info(
                "Skipping item %s — answer-key disagreement (--require-agreement)",
                result.item.item_id,
            )
            continue

        passed.append(item_to_dict(result.item))

    # Report
    logger.info("=" * 60)
    logger.info("Generation complete for %s", args.caps_ref)
    logger.info("  Attempted : %d", args.n_items)
    logger.info("  Generated : %d", len(results))
    logger.info("  Passed    : %d", len(passed))
    logger.info("  Failed    : %d (validator)", failed)
    logger.info("  Disagreed : %d (answer-key)", disagreed)
    logger.info("=" * 60)

    if not passed:
        logger.warning("No items passed — nothing written.")
        return 1

    # Write to seed file
    if args.dry_run:
        logger.info("DRY RUN — not writing to %s", args.output)
        print(json.dumps(passed[:3], indent=2, ensure_ascii=False))
        return 0

    existing = load_seed_file(args.output)
    existing_ids = {item.get("item_id") for item in existing}
    new_items = [i for i in passed if i.get("item_id") not in existing_ids]
    combined = existing + new_items

    save_seed_file(args.output, combined)
    logger.info(
        "Wrote %d new items (total %d) → %s",
        len(new_items), len(combined), args.output,
    )
    return 0


if __name__ == "__main__":
    args = parse_args()
    sys.exit(asyncio.run(main(args)))
