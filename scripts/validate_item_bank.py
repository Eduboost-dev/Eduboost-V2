#!/usr/bin/env python
"""
validate_item_bank.py — P2-05
================================
Offline validation runner.  Reads the canonical seed JSON file, runs all
8 ItemValidator rules against every item, and prints a per-item pass/fail
report with item IDs.

Usage:
    python scripts/validate_item_bank.py \\
        [--input data/caps/grade4_maths_item_bank.json] \\
        [--topic-map data/caps/caps_topic_map_grade4_maths.json] \\
        [--caps-ref 4.M.1.1] \\
        [--only-approved] \\
        [--fail-fast] \\
        [--json-report output/validation_report.json]

Exit codes:
    0 — all items passed
    1 — one or more items failed (use in CI to block merge)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.domain.item_schema import ItemCreate  # noqa: E402
from app.modules.diagnostics.item_validator import (  # noqa: E402
    ItemValidationError,
    ItemValidator,
    ValidationReport,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("validate_item_bank")

DEFAULT_INPUT = Path("data/caps/grade4_maths_item_bank.json")
DEFAULT_TOPIC_MAP = Path("data/caps/caps_topic_map_grade4_maths.json")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate all items in the CAPS item bank seed file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--topic-map", type=Path, default=DEFAULT_TOPIC_MAP)
    parser.add_argument(
        "--caps-ref",
        help="Only validate items with this CAPS reference (default: all)",
    )
    parser.add_argument(
        "--only-approved",
        action="store_true",
        help="Only validate items with review_status=approved",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after first failed item",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        help="Write detailed JSON report to this path",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_items(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("items", [])


def print_banner(title: str, width: int = 70) -> None:
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_rule_row(result) -> None:
    status = "✓" if result.passed else "✗"
    print(f"      {status} [{result.rule}] {result.message}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # Load inputs
    if not args.input.exists():
        logger.error("Seed file not found: %s", args.input)
        return 1
    if not args.topic_map.exists():
        logger.error("Topic map not found: %s", args.topic_map)
        return 1

    with open(args.topic_map, encoding="utf-8") as f:
        topic_map = json.load(f)

    raw_items = load_items(args.input)
    logger.info("Loaded %d items from %s", len(raw_items), args.input)

    # Filtering
    if args.caps_ref:
        raw_items = [i for i in raw_items if i.get("caps_ref") == args.caps_ref]
        logger.info("Filtered to %d items with caps_ref=%s", len(raw_items), args.caps_ref)
    if args.only_approved:
        raw_items = [i for i in raw_items if i.get("review_status") == "approved"]
        logger.info("Filtered to %d approved items", len(raw_items))

    if not raw_items:
        logger.warning("No items to validate after filtering.")
        return 0

    validator = ItemValidator(topic_map=topic_map)

    # Validation loop
    reports: list[ValidationReport] = []
    passed_count = 0
    failed_count = 0

    print_banner(f"EduBoost SA — Item Bank Validation ({args.input})")
    print(f"  Items to validate : {len(raw_items)}")
    print(f"  Topic map         : {args.topic_map}")
    print(f"  Run at            : {datetime.now(tz=timezone.utc).isoformat()}")
    print()

    for raw in raw_items:
        item_id = raw.get("item_id", "unknown")
        caps_ref = raw.get("caps_ref", "unknown")

        try:
            item = ItemCreate(**raw)
        except Exception as exc:
            print(f"  [PARSE ERROR] {item_id} ({caps_ref}): {exc}")
            failed_count += 1
            if args.fail_fast:
                break
            continue

        report = validator.validate(item)
        reports.append(report)

        if report.passed:
            passed_count += 1
            print(f"  ✓ PASS  {item_id}  ({caps_ref})")
        else:
            failed_count += 1
            print(f"  ✗ FAIL  {item_id}  ({caps_ref})")
            for rule_result in report.failures:
                print_rule_row(rule_result)
            if args.fail_fast:
                print("\n  [fail-fast] Stopping after first failure.")
                break

    # Summary
    print()
    print_banner("Validation Summary")
    total = passed_count + failed_count
    print(f"  Total validated : {total}")
    print(f"  Passed          : {passed_count}")
    print(f"  Failed          : {failed_count}")
    pass_rate = (passed_count / total * 100) if total else 0
    print(f"  Pass rate       : {pass_rate:.1f}%")
    print()

    # Coverage by caps_ref
    caps_ref_counts: dict[str, dict] = {}
    for report in reports:
        # Rebuild from raw items since report only has item_id
        pass  # coverage breakdown is done from raw_items below

    caps_counts: dict[str, int] = {}
    caps_passed: dict[str, int] = {}
    for raw, report in zip(raw_items[:len(reports)], reports):
        ref = raw.get("caps_ref", "unknown")
        caps_counts[ref] = caps_counts.get(ref, 0) + 1
        if report.passed:
            caps_passed[ref] = caps_passed.get(ref, 0) + 1

    print("  Coverage by CAPS Ref:")
    for ref in sorted(caps_counts):
        n = caps_counts[ref]
        p = caps_passed.get(ref, 0)
        bar = "█" * p + "░" * (n - p)
        print(f"    {ref:12s}  {p:3d}/{n:3d}  {bar}")
    print()

    # Optional JSON report
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_report, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "generated_at": datetime.now(tz=timezone.utc).isoformat(),
                    "source": str(args.input),
                    "total": total,
                    "passed": passed_count,
                    "failed": failed_count,
                    "pass_rate": pass_rate,
                    "reports": [r.as_dict() for r in reports],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info("JSON report written to %s", args.json_report)

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
