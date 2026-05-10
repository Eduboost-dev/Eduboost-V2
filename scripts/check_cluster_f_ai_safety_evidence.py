#!/usr/bin/env python3
"""Validate Cluster F AI/CAPS/safety evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "tests/unit/test_ai_output_schema_contract.py",
    "tests/unit/test_llm_provider_fallback_contract.py",
    "docs/ai/ai_output_schema_contract.md",
    "docs/ai/llm_provider_fallback_contract.md",
    "scripts/check_ai_output_schema_contract.py",
    "scripts/check_llm_provider_fallback_contract.py",
    "tests/unit/test_diagnostic_generation_safety_contract.py",
    "tests/unit/test_ai_prompt_input_contract.py",
    "docs/ai/diagnostic_generation_safety_contract.md",
    "docs/ai/ai_prompt_input_contract.md",
    "scripts/check_diagnostic_generation_safety_contract.py",
    "scripts/check_ai_prompt_input_contract.py",
    "scripts/check_caps_alignment_contract.py",
    "scripts/check_ai_safety_boundary_contract.py",
    "docs/ai/caps_alignment_contract.md",
    "docs/ai/ai_safety_boundary_contract.md",
    "tests/unit/test_caps_alignment_contract.py",
    "tests/unit/test_ai_safety_boundary_contract.py",
)

CONTENT_REQUIREMENTS = {
    "docs/ai/ai_output_schema_contract.md": (
        "AI Output Schema Contract",
        "safe educational redirection",
    ),
    "docs/ai/llm_provider_fallback_contract.md": (
        "LLM Provider Fallback Contract",
        "fallback must fail closed when no safe provider is available",
    ),
    "docs/ai/diagnostic_generation_safety_contract.md": (
        "Diagnostic Generation Safety Contract",
        "every item must map to the diagnostic objective",
    ),
    "docs/ai/ai_prompt_input_contract.md": (
        "AI Prompt Input Contract",
        "prompts must avoid cross-learner data leakage",
    ),
    "Makefile": (
        "caps-alignment-contract-check:",
        "ai-safety-boundary-check:",
        "ai-prompt-input-contract-check:",
        "diagnostic-generation-safety-check:",
        "llm-provider-fallback-contract-check:",
        "ai-output-schema-contract-check:",
    ),
    "docs/ai/caps_alignment_contract.md": (
        "CAPS Alignment Contract",
        "generated diagnostics must be objective-bound",
    ),
    "docs/ai/ai_safety_boundary_contract.md": (
        "AI Safety Boundary Contract",
        "Unsafe requests must be refused",
    ),
}


@dataclass(frozen=True)
class ClusterFResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterFResult]:
    results: list[ClusterFResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(ClusterFResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterFResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster F AI safety evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
