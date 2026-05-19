#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITICAL = [
    "app/services/diagnostic_route_integrity.py",
    "app/services/diagnostic_session_integrity.py",
    "app/api_v2_routers/diagnostics.py",
    "scripts/patch_diagnostics_session_binding.py",
    "scripts/check_diagnostics_session_binding.py",
    "tests/unit/test_diagnostic_route_integrity.py",
    "tests/integration/test_diagnostics_session_binding_routes.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Diagnostics served-item/session/CAPS binding check")

    router = read("app/api_v2_routers/diagnostics.py")
    expected_router_tokens = [
        "validate_adaptive_diagnostic_response",
        "DiagnosticIntegrityError",
        "caps_ref does not match recovered diagnostic session",
        "list_by_caps_ref(session_caps_ref",
        "caps_ref: str | None = None",
    ]
    for token in expected_router_tokens:
        if token in router:
            print(f"- PASS diagnostics router contains {token}")
        else:
            failures.append(f"diagnostics router missing {token}")

    helper = read("app/services/diagnostic_route_integrity.py")
    for token in ["served_items_from_snapshot", "assert_caps_ref_matches_session", "validate_session_served_item_binding"]:
        if token in helper:
            print(f"- PASS diagnostic route integrity helper contains {token}")
        else:
            failures.append(f"diagnostic route integrity helper missing {token}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    pytest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_diagnostic_route_integrity.py",
            "tests/integration/test_diagnostics_session_binding_routes.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(pytest_result.stdout)
    if pytest_result.returncode == 0:
        print("- PASS diagnostics session binding focused tests")
    else:
        failures.append("diagnostics session binding focused tests failed")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff diagnostics session binding check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS diagnostics served-item/session/CAPS binding check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
