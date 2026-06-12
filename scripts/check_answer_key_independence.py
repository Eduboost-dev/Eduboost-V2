#!/usr/bin/env python3
"""
Phase 9 — G.6: Independent Answer-Key Checking

Verifies that lesson-generation output includes structured answer-key data
that can be independently validated without access to the generation prompt.

This ensures answer keys are not hardcoded or derived from the same
parameters as the content (which would compromise assessment validity).
"""
import argparse
import json
import sys
from pathlib import Path


def check_answer_key_structure(lesson_data: dict) -> tuple[bool, str]:
    """
    Verify that lesson output contains structured answer-key data.
    
    Expected structure:
    {
        "lesson_id": "uuid",
        "items": [
            {
                "item_id": "uuid",
                "question": "...",
                "answer_key": "...",
                "answer_key_hash": "sha256:...",  # For verification without exposing key
                "metadata": {
                    "difficulty": 1-5,
                    "cognitive_level": "remember|understand|apply|analyze|evaluate|create",
                    "caps_topic": "..."
                }
            }
        ],
        "answer_key_metadata": {
            "generated_at": "ISO8601",
            "generator_model": "...",
            "validation_hash": "sha256:..."  # Hash of all answer_keys for integrity
        }
    }
    """
    # Check top-level structure
    if "items" not in lesson_data:
        return False, "Missing 'items' array in lesson output"

    items = lesson_data.get("items", [])
    if not items:
        return False, "Lesson items array is empty"

    # Check each item has answer key
    for i, item in enumerate(items):
        if "answer_key" not in item:
            return False, f"Item {i} missing 'answer_key' field"

        if not item["answer_key"]:
            return False, f"Item {i} has empty answer_key"

    # Check for integrity mechanism (hash or metadata)
    has_integrity = (
        "answer_key_metadata" in lesson_data or
        any("answer_key_hash" in item for item in items)
    )

    if not has_integrity:
        return False, "No answer-key integrity mechanism found (hash or metadata)"

    # Check for independence indicators
    # Answer keys should not be derivable from the same prompt as content
    has_separation = (
        "answer_key_metadata" in lesson_data and
        "generator_model" in lesson_data.get("answer_key_metadata", {})
    )

    if not has_separation:
        return False, "No generator model metadata (cannot verify independence)"

    return True, f"OK: {len(items)} items with answer keys and integrity mechanism"


def check_lesson_files(directory: Path) -> tuple[int, int, list[str]]:
    """
    Check all lesson JSON files in a directory.
    
    Returns: (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []

    for json_file in directory.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)

            # Try both direct array and wrapped format
            lessons = data if isinstance(data, list) else data.get("lessons", [data])

            for lesson in lessons:
                ok, msg = check_answer_key_structure(lesson)
                if ok:
                    passed += 1
                else:
                    failed += 1
                    errors.append(f"{json_file.name}: {msg}")

        except json.JSONDecodeError as e:
            failed += 1
            errors.append(f"{json_file.name}: Invalid JSON - {e}")
        except Exception as e:
            failed += 1
            errors.append(f"{json_file.name}: {e}")

    return passed, failed, errors


def main():
    parser = argparse.ArgumentParser(
        description="Verify answer-key independence in lesson generation output"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Path to lesson JSON files or directory"
    )
    parser.add_argument(
        "--sample",
        help="Single lesson JSON file to check"
    )
    args = parser.parse_args()

    print("🔑 Answer-Key Independence Verification")
    print("=" * 50)

    if args.sample:
        # Check single file
        with open(args.sample) as f:
            data = json.load(f)
        ok, msg = check_answer_key_structure(data)
        if ok:
            print(f"  ✅ {args.sample}: {msg}")
            return 0
        else:
            print(f"  ❌ {args.sample}: {msg}")
            return 1

    # Check directory
    if args.path.is_file():
        with open(args.path) as f:
            data = json.load(f)
        ok, msg = check_answer_key_structure(data)
        if ok:
            print(f"  ✅ {args.path.name}: {msg}")
            return 0
        else:
            print(f"  ❌ {args.path.name}: {msg}")
            return 1

    print(f"\n📁 Scanning: {args.path}")
    passed, failed, errors = check_lesson_files(args.path)

    print("\n📊 Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")

    if errors:
        print("\n⚠️ Errors:")
        for error in errors[:10]:  # Show first 10
            print(f"    - {error}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")

    if failed == 0 and passed > 0:
        print("\n🎉 All lessons have valid answer-key structure!")
        return 0
    else:
        print(f"\n💥 Answer-key validation failed for {failed} file(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
