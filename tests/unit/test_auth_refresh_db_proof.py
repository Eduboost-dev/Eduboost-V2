from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_refresh_db_proof import build_status, evidence_fields, output_has_skips, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_auth_refresh_db_proof_defaults_to_external_blocked_without_dsn(monkeypatch):
    monkeypatch.delenv("AUTH_REFRESH_DB_PROOF_DSN", raising=False)
    status = build_status(run_pytest=False)
    assert status.status == "auth-refresh-db-proof-external-blocked"
    assert "AUTH_REFRESH_DB_PROOF_DSN is not set" in status.blockers


def test_auth_refresh_db_evidence_template_is_pending_by_default():
    fields = evidence_fields()
    assert fields
    assert any(not field.valid and field.reason == "pending" for field in fields)


def test_skip_detection_rejects_skipped_output():
    assert output_has_skips("1 passed, 1 skipped")
    assert not output_has_skips("2 passed in 0.10s")


def test_auth_refresh_db_status_writes_reports():
    status = write_status(run_pytest=False)
    assert (ROOT / "docs/release/auth_refresh_db_proof_status.json").exists()
    assert (ROOT / "docs/release/auth_refresh_db_proof_status.md").exists()
    assert status.status == "auth-refresh-db-proof-external-blocked"


def test_auth_refresh_db_release_check_fails_without_real_db():
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_refresh_db_proof.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode != 0
    assert "release mode requires accepted auth refresh DB proof" in result.stdout


def test_auth_refresh_db_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_refresh_db_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_refresh_db_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-refresh-db-proof-status:" in source
    assert "auth-refresh-db-proof-check:" in source
    assert "backend-implementation-2671-2710-full-check:" in source
