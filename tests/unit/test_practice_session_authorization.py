from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.practice import router as practice_router
from app.modules.practice.router import PracticeResponseRequest


@pytest.fixture(autouse=True)
def clear_practice_sessions():
    practice_router._SESSIONS.clear()
    yield
    practice_router._SESSIONS.clear()


@pytest.mark.asyncio
async def test_next_practice_item_rejects_wrong_session_owner():
    learner_id = str(uuid4())
    session_id = "session-1"
    practice_router._SESSIONS[session_id] = {
        "learner_id": learner_id,
        "owner_subject": learner_id,
        "items": [str(uuid4())],
        "cursor": 0,
        "responses": [],
    }

    with pytest.raises(HTTPException) as exc:
        await practice_router.next_practice_item(
            session_id,
            current_user={"sub": str(uuid4()), "role": "learner"},
            db=object(),
        )

    assert exc.value.status_code == 403
    assert practice_router._SESSIONS[session_id]["cursor"] == 0


@pytest.mark.asyncio
async def test_next_practice_item_requires_consent_for_session_owner(monkeypatch):
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = "session-2"
    practice_router._SESSIONS[session_id] = {
        "learner_id": learner_id,
        "owner_subject": learner_id,
        "items": [item_id],
        "cursor": 0,
        "responses": [],
    }
    calls = []

    async def allow_consent(db, current_user, checked_learner_id):
        calls.append((db, current_user, checked_learner_id))

    monkeypatch.setattr(practice_router, "require_active_consent_for_current_user", allow_consent)

    result = await practice_router.next_practice_item(
        session_id,
        current_user={"sub": learner_id, "role": "learner", "learner_id": learner_id},
        db=object(),
    )

    assert result == {"completed": False, "item_id": item_id}
    assert calls and calls[0][2] == learner_id


@pytest.mark.asyncio
async def test_respond_practice_rejects_wrong_session_owner_without_advancing():
    learner_id = str(uuid4())
    session_id = "session-3"
    practice_router._SESSIONS[session_id] = {
        "learner_id": learner_id,
        "owner_subject": learner_id,
        "items": [str(uuid4())],
        "cursor": 0,
        "responses": [],
    }

    with pytest.raises(HTTPException) as exc:
        await practice_router.respond_practice(
            session_id,
            PracticeResponseRequest(item_id=uuid4(), correct=True),
            current_user={"sub": str(uuid4()), "role": "learner"},
            db=object(),
        )

    assert exc.value.status_code == 403
    assert practice_router._SESSIONS[session_id]["cursor"] == 0
    assert practice_router._SESSIONS[session_id]["responses"] == []


@pytest.mark.asyncio
async def test_respond_practice_requires_consent_before_advancing(monkeypatch):
    learner_id = str(uuid4())
    item_id = uuid4()
    session_id = "session-4"
    practice_router._SESSIONS[session_id] = {
        "learner_id": learner_id,
        "owner_subject": learner_id,
        "items": [str(item_id)],
        "cursor": 0,
        "responses": [],
    }
    calls = []

    async def allow_consent(db, current_user, checked_learner_id):
        calls.append((db, current_user, checked_learner_id))

    monkeypatch.setattr(practice_router, "require_active_consent_for_current_user", allow_consent)

    result = await practice_router.respond_practice(
        session_id,
        PracticeResponseRequest(item_id=item_id, correct=False, response="B"),
        current_user={"sub": learner_id, "role": "learner", "learner_id": learner_id},
        db=object(),
    )

    assert result["accepted"] is True
    assert calls and calls[0][2] == learner_id
    assert practice_router._SESSIONS[session_id]["cursor"] == 1
    assert practice_router._SESSIONS[session_id]["responses"][0]["correct"] is False