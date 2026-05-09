"""HTTP contract tests for POPIA learner export authorization."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import popia as popia_router


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, learner_id: str) -> SimpleNamespace | None:
        if learner_id == "missing-learner":
            return None
        return SimpleNamespace(
            id=learner_id,
            guardian_id="guardian-1",
            pseudonym_id=f"pseudo-{learner_id}",
        )


class FakePOPIADataRightsService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def build_learner_export(self, learner_id: str, current_user: dict, export_format: str = "json") -> dict:
        return {"learner_id": learner_id, "export_format": export_format, "records": []}


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def popia_export_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(popia_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(popia_router, "POPIADataRightsService", FakePOPIADataRightsService)
    app.dependency_overrides[popia_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_popia_export_allows_admin_read() -> None:
    app.dependency_overrides[popia_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/popia/data-export/learner-1")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["learner_id"] == "learner-1"


@pytest.mark.integration
def test_popia_export_allows_assigned_guardian_read() -> None:
    app.dependency_overrides[popia_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/popia/data-export/learner-1")

    assert response.status_code == 200


@pytest.mark.integration
def test_popia_export_allows_learner_self_read() -> None:
    app.dependency_overrides[popia_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).get("/api/v2/popia/data-export/learner-1")

    assert response.status_code == 200


@pytest.mark.integration
def test_popia_export_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[popia_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/popia/data-export/learner-1")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_popia_export_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/popia/data-export/learner-1")

    assert response.status_code == 401


@pytest.mark.integration
def test_popia_export_preserves_not_found() -> None:
    app.dependency_overrides[popia_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/popia/data-export/missing-learner")

    assert response.status_code == 404
