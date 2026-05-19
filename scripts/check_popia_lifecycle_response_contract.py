#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.proof_pytest import run_pytest_proof  # noqa: E402

CRITICAL = [
    "app/services/popia_consent_lifecycle_adapter.py",
    "app/api_v2_routers/popia.py",
    "tests/integration/test_popia_lifecycle_response_contract.py",
    "tests/unit/test_popia_lifecycle_response_contracts.py",
    "scripts/check_popia_lifecycle_response_contract.py",
    "scripts/proof_pytest.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("POPIA lifecycle response-contract check")

    adapter = read("app/services/popia_consent_lifecycle_adapter.py")
    for token in ("_coerce_consent_record", "ConsentRecord", "fallback_state=ConsentState.DENIED", "fallback_state=ConsentState.WITHDRAWN"):
        if token in adapter:
            print(f"- PASS adapter contains {token}")
        else:
            failures.append(f"adapter missing {token}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("IN_SUBPROCESS_CHECK"):
        try:
            run_pytest_proof(
                [
                    "-c",
                    "pytest.ini",
                    "tests/integration/test_popia_lifecycle_response_contract.py",
                    "tests/unit/test_popia_lifecycle_response_contracts.py",
                    "-q",
                    "--no-cov",
                    "--tb=short",
                ],
                root=ROOT,
                require_no_skips=True,
                extra_env={"IN_SUBPROCESS_CHECK": "1"},
            )
            print("- PASS POPIA lifecycle HTTP response-contract tests with zero skips")
        except Exception as exc:
            failures.append(str(exc))

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff POPIA lifecycle response-contract check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS POPIA lifecycle response-contract check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
