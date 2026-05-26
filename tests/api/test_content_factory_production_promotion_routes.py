"""API tests for production promotion routes."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_unauthenticated_production_gate_rejected(client: TestClient) -> None:
    """Unauthenticated production gate rejected."""
    response = client.get("/api/v2/admin/content-factory/scopes/test_scope/production-gate")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_non_admin_production_gate_rejected(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Non-admin production gate rejected."""
    response = client.get("/api/v2/admin/content-factory/scopes/test_scope/production-gate", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_fetch_production_gate(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can fetch production gate."""
    response = client.get("/api/v2/admin/content-factory/scopes/test_scope/production-gate", headers=admin_auth_headers)
    assert response.status_code in [200, 404]  # 404 if scope doesn't exist, 200 if it does


@pytest.mark.asyncio
async def test_admin_can_dry_run_promotion(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can dry-run promotion."""
    response = client.post("/api/v2/admin/content-factory/scopes/test_scope/dry-run-promotion", headers=admin_auth_headers)
    assert response.status_code in [200, 409]  # 409 if gate fails


@pytest.mark.asyncio
async def test_promote_production_rejects_missing_confirmation(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Promote production rejects missing confirmation."""
    response = client.post(
        "/api/v2/admin/content-factory/scopes/test_scope/promote-production",
        headers=admin_auth_headers,
        json={"layers": None, "confirmation": ""},
    )
    assert response.status_code == 422  # Validation error for missing confirmation


@pytest.mark.asyncio
async def test_promote_production_rejects_wrong_confirmation(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Promote production rejects wrong confirmation."""
    response = client.post(
        "/api/v2/admin/content-factory/scopes/test_scope/promote-production",
        headers=admin_auth_headers,
        json={"layers": None, "confirmation": "WRONG_CONFIRMATION"},
    )
    assert response.status_code == 409  # Confirmation mismatch


@pytest.mark.asyncio
async def test_promote_production_rejects_blocked_gate(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Promote production rejects blocked gate."""
    response = client.post(
        "/api/v2/admin/content-factory/scopes/test_scope/promote-production",
        headers=admin_auth_headers,
        json={"layers": None, "confirmation": "PROMOTE test_scope TO PRODUCTION"},
    )
    assert response.status_code == 409  # Gate blocked


@pytest.mark.asyncio
async def test_admin_can_list_promotion_events(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can list promotion events."""
    response = client.get("/api/v2/admin/content-factory/promotion-events", headers=admin_auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_fetch_promotion_event(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can fetch promotion event."""
    promotion_event_id = uuid.uuid4()
    response = client.get(f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}", headers=admin_auth_headers)
    assert response.status_code == 404  # Event doesn't exist yet


@pytest.mark.asyncio
async def test_admin_can_fetch_promotion_event_items(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can fetch promotion event items."""
    promotion_event_id = uuid.uuid4()
    response = client.get(f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/items", headers=admin_auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_verify_promotion_event(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can verify promotion event."""
    promotion_event_id = uuid.uuid4()
    response = client.post(f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/verify", headers=admin_auth_headers)
    assert response.status_code == 404  # Event doesn't exist yet


@pytest.mark.asyncio
async def test_admin_can_rollback_promotion_event(client: TestClient, admin_auth_headers: dict[str, str]) -> None:
    """Admin can rollback promotion event."""
    promotion_event_id = uuid.uuid4()
    response = client.post(
        f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/rollback",
        headers=admin_auth_headers,
        json={"reason": "test rollback"},
    )
    assert response.status_code == 404  # Event doesn't exist yet
