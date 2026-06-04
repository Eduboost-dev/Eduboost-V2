from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.domain.content_coverage import ContentLayer, CoverageTarget
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_scope_content import validate_scope

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_validator_passes_grade4_maths_active_scope() -> None:
    result = validate_scope("grade4_mathematics_en", strict=True)

    assert result.passed is True
    assert result.skipped is False
    assert result.item_counts == {"4.M.1.1": 40, "4.M.1.2": 40, "4.M.1.3": 40}
    assert result.lesson_counts == {"4.M.1.1": 8, "4.M.1.2": 8, "4.M.1.3": 8}


def test_validator_skips_review_scope_in_non_strict_mode() -> None:
    result = validate_scope("grade5_mathematics_en", strict=False)

    assert result.passed is True
    assert result.skipped is True
    assert result.status == "review"
    assert result.item_counts == {}
    assert result.lesson_counts == {}


def test_validator_fails_active_scope_below_pilot_targets(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = ContentScopeRegistry()
    scope = registry.get_scope("grade4_mathematics_en")

    def inflated_targets(scope_id: str) -> list[CoverageTarget]:
        assert scope_id == scope.scope_id
        return [
            CoverageTarget(
                scope_id=scope.scope_id,
                caps_ref=caps_ref,
                targets={
                    f"{ContentLayer.DIAGNOSTIC_ITEMS.value}.approved": 41,
                    f"{ContentLayer.LESSONS.value}.approved": 9,
                },
            )
            for caps_ref in scope.caps_refs
        ]

    monkeypatch.setattr(registry, "get_scope_targets", inflated_targets)

    result = validate_scope("grade4_mathematics_en", strict=True, registry=registry)

    assert result.passed is False
    assert any("diagnostic_items approved target unmet: 40/41" in error for error in result.errors)
    assert any("lessons approved target unmet: 8/9" in error for error in result.errors)


def test_source_manifest_planned_requirements_cover_all_registered_scopes() -> None:
    manifest = json.loads((REPO_ROOT / "data/caps/source_documents/manifest.json").read_text(encoding="utf-8"))
    registry_scope_ids = {scope.scope_id for scope in ContentScopeRegistry().list_scopes()}
    planned_requirements = manifest.get("planned_source_requirements") or {}
    covered_scope_ids: set[str] = set()

    if isinstance(planned_requirements, dict):
        covered_scope_ids.update(planned_requirements.get("scope_ids", []))
    else:
        for requirement in planned_requirements:
            covered_scope_ids.update(requirement.get("scope_ids", []))

    assert registry_scope_ids <= covered_scope_ids
