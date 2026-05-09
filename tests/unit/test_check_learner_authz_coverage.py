from __future__ import annotations

import pytest

from scripts.check_learner_authz_coverage import main


@pytest.mark.unit
def test_learner_authz_coverage_check_passes_current_routes() -> None:
    assert main() == 0
