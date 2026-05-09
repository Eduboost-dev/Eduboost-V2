from __future__ import annotations

import subprocess
import sys

import pytest

from scripts.check_learner_authz_coverage import ALLOWLIST, main


@pytest.mark.unit
def test_learner_authz_coverage_check_passes_current_routes() -> None:
    assert main() == 0


@pytest.mark.unit
def test_learner_authz_coverage_allowlist_documents_boundary_routes() -> None:
    assert ("auth.py", "POST", "/dev-session") in ALLOWLIST
    assert ("consent_renewal.py", "POST", "/trigger-renewal-reminders") in ALLOWLIST
    assert ("ether.py", "GET", "/onboarding/questions") in ALLOWLIST
    assert ("gamification.py", "GET", "/leaderboard") in ALLOWLIST


@pytest.mark.unit
def test_learner_authz_coverage_script_runs_directly() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_learner_authz_coverage.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Learner authorization coverage check" in result.stdout
    assert "ALLOW auth.py POST /dev-session" in result.stdout
