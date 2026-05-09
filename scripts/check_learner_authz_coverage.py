#!/usr/bin/env python3
"""Fail if learner-scoped routes lack an authorization/authentication marker."""
from __future__ import annotations

from scripts.generate_learner_authz_matrix import collect_rows


ALLOWLIST = {
    # Catalog/auth-boundary endpoints with separate docs/tests.
    ("assessments.py", "GET", "/"),
    ("assessments.py", "GET", ""),
    ("onboarding.py", "GET", "/questions"),
    # Public ranking endpoint; this is aggregate gamification data and not learner-object scoped.
    ("gamification.py", "GET", "/leaderboard"),
}


def main() -> int:
    rows = collect_rows()
    missing = [
        row
        for row in rows
        if row.status == "missing" and (row.router, row.method, row.path) not in ALLOWLIST
    ]

    print("Learner authorization coverage check")
    for row in rows:
        status = "ALLOW" if (row.router, row.method, row.path) in ALLOWLIST else row.status.upper()
        print(f"- {status} {row.router} {row.method} {row.path} -> {row.function} [{row.authz_marker}]")

    if missing:
        print("\nMissing learner authorization coverage:")
        for row in missing:
            print(f"- {row.router} {row.method} {row.path} -> {row.function}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
