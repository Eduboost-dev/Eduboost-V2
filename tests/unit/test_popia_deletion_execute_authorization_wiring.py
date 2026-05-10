"""Tests for POPIA deletion-execute authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_deletion_execute_authorizes_before_enqueue() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "popia.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def execute_learner_deletion", maxsplit=1)[1].split(
        "async def _run",
        maxsplit=1,
    )[0]

    assert "require_learner_write_for_current_user(current_user, learner_id)" in block
