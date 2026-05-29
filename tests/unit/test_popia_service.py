from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import popia_service
from app.services.popia_service import (
    POPIA_ERASURE_GRACE_DAYS,
    POPIA_ERASURE_REVIEW_SLA_DAYS,
    POPIA_EXPORT_SLA_DAYS,
    POPIADataRightsService,
    RightsRequestStatus,
)


@pytest.mark.unit
def test_popia_service_init_stores_dependencies():
    """Verify constructor stores database session and repositories."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    assert service.db is db
    assert service.learners is not None
    assert service.audit is not None
    assert service.consent is not None


class FakeService(POPIADataRightsService):
    def __init__(self, learner):
        self.learner = learner

    async def load_learner_for_read(self, learner_id, current_user):
        return self.learner

    async def load_learner_for_write(self, learner_id, current_user):
        return self.learner


@pytest.mark.asyncio
async def test_erasure_requires_guardian_or_admin() -> None:
    svc = FakeService(SimpleNamespace(id="learner-1", guardian_id="guardian-1", deletion_requested_at=None))
    with pytest.raises(HTTPException) as exc:
        await svc.request_erasure("learner-1", {"sub": "guardian-2", "role": "parent"})
    assert exc.value.status_code == 403


@pytest.mark.unit
def test_popia_constants_defined():
    """Verify POPIA SLA constants are defined correctly."""
    assert POPIA_EXPORT_SLA_DAYS == 30
    assert POPIA_ERASURE_REVIEW_SLA_DAYS == 30
    assert POPIA_ERASURE_GRACE_DAYS == 30


@pytest.mark.unit
def test_rights_request_status_dataclass():
    """Verify RightsRequestStatus dataclass is properly defined."""
    status = RightsRequestStatus(
        request_type="export",
        status="completed",
        learner_id="learner-123",
        requested_at="2024-01-01T00:00:00Z",
        due_at="2024-01-31T00:00:00Z",
        audit_event_type="data_export.requested",
        requires_admin_review=False,
        reason="user_request",
    )
    assert status.request_type == "export"
    assert status.status == "completed"
    assert status.learner_id == "learner-123"
    assert status.requires_admin_review is False
    assert status.reason == "user_request"


@pytest.mark.unit
def test_rights_request_status_defaults():
    """Verify RightsRequestStatus has correct defaults."""
    status = RightsRequestStatus(
        request_type="export",
        status="completed",
        learner_id="learner-123",
        requested_at="2024-01-01T00:00:00Z",
        due_at="2024-01-31T00:00:00Z",
        audit_event_type="data_export.requested",
    )
    assert status.requires_admin_review is False
    assert status.reason is None


@pytest.mark.unit
def test_to_csv_converts_payload():
    """Verify _to_csv converts payload to CSV format."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    payload = {
        "learner": {"id": "learner-123", "name": "Test"},
        "diagnostic_sessions": [{"id": "session-1", "theta": 0.5}],
        "guardian": {"id": "guardian-1", "email": "test@example.com"},
    }
    csv_output = service._to_csv(payload)
    assert "learner,id,learner-123" in csv_output
    assert "learner,name,Test" in csv_output
    assert "diagnostic_sessions,id,session-1" in csv_output
    assert "guardian,id,guardian-1" in csv_output


@pytest.mark.unit
def test_status_creates_rights_request_status():
    """Verify _status creates RightsRequestStatus with correct values."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    with patch("app.services.popia_service._now") as mock_now:
        mock_now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_now.return_value.__add__ = lambda self, days: SimpleNamespace(isoformat=lambda: "2024-01-31T00:00:00Z")
        status = service._status("export", "completed", "learner-123", 30, "data_export.requested")
        assert status.request_type == "export"
        assert status.status == "completed"
        assert status.learner_id == "learner-123"
        assert status.audit_event_type == "data_export.requested"


@pytest.mark.unit
def test_status_with_optional_params():
    """Verify _status handles optional parameters."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    with patch("app.services.popia_service._now") as mock_now:
        mock_now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_now.return_value.__add__ = lambda self, days: SimpleNamespace(isoformat=lambda: "2024-01-31T00:00:00Z")
        status = service._status(
            "restriction",
            "accepted",
            "learner-123",
            30,
            "processing.restricted",
            requires_admin_review=True,
            reason="user_request",
        )
        assert status.requires_admin_review is True
        assert status.reason == "user_request"


@pytest.mark.unit
async def test_requires_admin_review_returns_false():
    """Verify requires_admin_review returns False (current policy)."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    learner = SimpleNamespace(id="learner-123")
    result = await service.requires_admin_review(learner)
    assert result is False


@pytest.mark.unit
def test_now_returns_utc_datetime():
    """Verify _now returns UTC datetime."""
    result = popia_service._now()
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc


@pytest.mark.unit
def test_iso_returns_isoformat_string():
    """Verify _iso returns ISO format string for datetime."""
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = popia_service._iso(dt)
    assert result == "2024-01-01T12:00:00+00:00"


@pytest.mark.unit
def test_iso_returns_none_for_none():
    """Verify _iso returns None for None input."""
    result = popia_service._iso(None)
    assert result is None


@pytest.mark.unit
def test_module_exports_all_public_symbols():
    """Verify __all__ contains expected public symbols."""
    expected = {
        "POPIADataRightsService",
        "POPIA_ERASURE_GRACE_DAYS",
        "POPIA_ERASURE_REVIEW_SLA_DAYS",
        "POPIA_EXPORT_SLA_DAYS",
        "RightsRequestStatus",
    }
    assert set(popia_service.__all__) == expected
