from __future__ import annotations

import pytest

from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.report_content_coverage import build_report
from scripts.curriculum.validate_scope_content import validate_scope
from scripts.curriculum.validate_source_manifest import generation_ready, validate_source_manifest


pytestmark = pytest.mark.unit


def test_source_manifest_validates_hashes_and_scope_links() -> None:
    result = validate_source_manifest()

    assert result.passed is True
    assert result.generation_ready_scope_ids == ["grade4_mathematics_en"]
    assert result.errors == []


def test_every_registered_scope_references_known_source_documents() -> None:
    registry = ContentScopeRegistry()
    result = validate_source_manifest(registry=registry)

    assert result.passed is True
    for scope in registry.list_scopes():
        assert scope.source_documents, scope.scope_id


def test_only_active_grade4_math_is_generation_ready() -> None:
    registry = ContentScopeRegistry()

    assert generation_ready("grade4_mathematics_en", registry=registry) is True
    assert generation_ready("grade5_mathematics_en", registry=registry) is False
    assert generation_ready("grade1_home_language_en", registry=registry) is False


def test_scope_validator_requires_source_readiness_for_active_scope() -> None:
    result = validate_scope("grade4_mathematics_en", strict=True)

    assert result.passed is True
    assert result.skipped is False


def test_coverage_report_exposes_generation_readiness_separately_from_visibility() -> None:
    report = build_report(strict_counts=True)

    assert report["summary"]["scopes.generation_ready"] == 1
    grade4 = next(row for row in report["scopes"] if row["scope_id"] == "grade4_mathematics_en")
    grade5 = next(row for row in report["scopes"] if row["scope_id"] == "grade5_mathematics_en")
    assert grade4["learner_visible"] is True
    assert grade4["generation_ready"] is True
    assert grade5["learner_visible"] is False
    assert grade5["generation_ready"] is False