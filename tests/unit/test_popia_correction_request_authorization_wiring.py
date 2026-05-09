"""Tests for POPIA correction-request authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_correction_request_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "popia.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def request_correction", maxsplit=1)[1].split(
        "@router.post",
        maxsplit=1,
    )[0]

    assert "learner = await LearnerRepository(db).get_by_id(learner_id)" in block
    assert "require_learner_write_for_current_user(current_user, learner_id)" in block
