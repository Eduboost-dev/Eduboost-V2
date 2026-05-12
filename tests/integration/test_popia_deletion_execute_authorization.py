from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for POPIA deletion-execute authorization."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import popia as popia_router


async def fake_enqueue_job(background_tasks, *, operation: str, payload: dict, handler):
    return {
        "job_id": "job-popia-purge-1",
        "operation": operation,
        "status": "queued",
        "payload": payload,
    }


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def popia_deletion_execute_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(popia_router, "enqueue_job", fake_enqueue_job)
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_popia_deletion_execute_allows_admin_write() -> None:
    app.dependency_overrides[popia_router.require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post("/api/v2/popia/deletion-execute/learner-1")

    assert response.status_code == 202
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["job_id"] == "job-popia-purge-1"


@pytest.mark.integration
def test_popia_deletion_execute_allows_guardian_with_claim() -> None:
    app.dependency_overrides[popia_router.require_parent_or_admin] = override_user(
        {"sub": "guardian-1", "role": "parent", "guardian_learner_ids": ["learner-1"]}
    )

    response = TestClient(app).post("/api/v2/popia/deletion-execute/learner-1")

    assert response.status_code == 202


@pytest.mark.integration
def test_popia_deletion_execute_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[popia_router.require_parent_or_admin] = override_user(
        {"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["learner-2"]}
    )

    response = TestClient(app).post("/api/v2/popia/deletion-execute/learner-1")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_popia_deletion_execute_rejects_missing_auth() -> None:
    response = TestClient(app).post("/api/v2/popia/deletion-execute/learner-1")

    assert response.status_code == 401
