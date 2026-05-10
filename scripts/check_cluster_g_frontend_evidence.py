#!/usr/bin/env python3
"""Validate Cluster G frontend journey evidence baseline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "scripts/generate_frontend_route_inventory.py",
    "scripts/check_frontend_route_inventory.py",
    "scripts/check_learner_vertical_journey_contract.py",
    "docs/frontend/frontend_route_inventory.md",
    "docs/frontend/learner_vertical_journey_contract.md",
    "tests/unit/test_frontend_route_inventory.py",
    "tests/unit/test_learner_vertical_journey_contract.py",
)

CONTENT_REQUIREMENTS = {
    "Makefile": (
        "frontend-route-inventory:",
        "frontend-route-inventory-check:",
        "learner-vertical-journey-contract-check:",
    ),
    "docs/frontend/frontend_route_inventory.md": (
        "Frontend Route Inventory",
        "Required Journey Areas",
    ),
    "docs/frontend/learner_vertical_journey_contract.md": (
        "Learner Vertical Journey Contract",
        "learner sees progress/mastery feedback",
    ),
}


@dataclass(frozen=True)
class ClusterGResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterGResult]:
    results: list[ClusterGResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(ClusterGResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterGResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster G frontend evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
