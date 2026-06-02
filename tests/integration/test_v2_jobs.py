from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration


from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers import lessons as lessons_router
from app.core.security import get_current_user, require_admin, require_parent_or_admin
from app.core.jobs import create_job, run_job
from app.models import UserRole


def _override_user():
    return {"sub": "00000000-0000-0000-0000-000000000002", "role": "admin", "jti": "test-jti"}


def _override_lesson_auth():
    now = datetime.now(timezone.utc)
    return AuthContext(
        user_id="00000000-0000-0000-0000-000000000002",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={
            "sub": "00000000-0000-0000-0000-000000000002",
            "role": "admin",
            "jti": "test-jti",
            "type": "access",
        },
        issued_at=now,
        expires_at=now + timedelta(minutes=15),
        jti="test-jti",
    )


def _client() -> TestClient:
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_parent_or_admin] = _override_user
    app.dependency_overrides[require_admin] = _override_user
    app.dependency_overrides[lessons_router.require_auth_context] = _override_lesson_auth
    return TestClient(app)


def teardown_module():
    app.dependency_overrides.clear()


async def _mock_enqueue(background_tasks, *, operation, handler, payload=None):
    job = await create_job(operation, payload=payload)
    await run_job(job["job_id"], handler)
    return job


def test_lesson_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.lessons.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.lessons.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.lessons.LessonService.generate_lesson_for_learner") as mock_gen:
        mock_gen.return_value = (
            type("LessonResponse", (), {"model_dump": lambda self, mode="json": {"id": "lesson-1"}}) (),
            False,
            "openai"
        )
        response = client.post("/v2/lessons/generate", json={"learner_id": "00000000-0000-0000-0000-000000000001", "subject": "Mathematics", "topic": "Fractions"})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["id"] == "lesson-1"


def test_study_plan_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.study_plans.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.study_plans.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.study_plans.StudyPlanServiceV2.generate_plan", new=AsyncMock(return_value={"plan_id": "plan-1", "learner_id": "learner-1"})), \
         patch("app.api_v2_routers.study_plans.AuditService.log_event", new=AsyncMock()), \
         patch("app.api_v2_routers.study_plans.TelemetryService.track_event_async", new=AsyncMock()):
        response = client.post("/v2/study-plans/generate/00000000-0000-0000-0000-000000000001", json={"gap_ratio": 0.4})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["plan_id"] == "plan-1"





def test_consent_renewal_job_flow():
    client = _client()
    with patch("app.core.database.AsyncSessionLocal") as session_factory, \
         patch("app.api_v2_routers.consent_renewal.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.consent_renewal.ConsentRenewalService.run", new=AsyncMock(return_value={"checked": 1, "reminded": 1, "failed": 0, "skipped_already_expired": 0})), \
         patch("app.api_v2_routers.consent_renewal.SendGridEmailGateway"):
        db = AsyncMock()
        session_factory.return_value.__aenter__.return_value = db
        response = client.post("/v2/admin/consent/trigger-renewal-reminders")
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["reminded"] == 1
