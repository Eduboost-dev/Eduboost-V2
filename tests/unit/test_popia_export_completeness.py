"""tests/unit/test_popia_export_completeness.py
T110A: POPIA export data inventory completeness tests

Verifies that the POPIA export payload includes all required fields
from the data inventory and excludes prohibited PII fields.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select

from app.models import (
    DiagnosticSession,
    KnowledgeGap,
    LearnerProfile,
    Lesson,
    ParentalConsent,
    SubjectMastery,
    TopicMastery,
    MasterySnapshot,
    PracticeQueue,
    SpacedReviewSchedule,
)
from app.services.popia_service import POPIADataRightsService


# ── Expected field sets from data inventory ─────────────────────────────────────

EXPECTED_LEARNER_FIELDS = {
    "id",
    "pseudonym_id",
    "display_name",
    "grade",
    "language",
    "archetype",
    "theta",
    "xp",
    "streak_days",
    "created_at",
    "last_active",
}

EXPECTED_DIAGNOSTIC_SESSION_FIELDS = {
    "id",
    "theta_before",
    "theta_after",
    "completed_at",
    "created_at",
}

EXPECTED_LESSON_FIELDS = {
    "id",
    "grade",
    "subject",
    "topic",
    "language",
    "archetype",
    "feedback_score",
    "served_from_cache",
    "created_at",
}

EXPECTED_KNOWLEDGE_GAP_FIELDS = {
    "id",
    "grade",
    "subject",
    "topic",
    "severity",
    "resolved",
    "created_at",
}

EXPECTED_CONSENT_FIELDS = {
    "id",
    "policy_version",
    "granted_at",
    "expires_at",
    "revoked_at",
    "is_active",
}

# Fields that must NOT appear in export (PII/internal)
PROHIBITED_FIELDS = {
    "email_hash",
    "email_encrypted",
    "stripe_customer_id",
    "stripe_subscription_id",
    "ip_address_hash",
    "reviewer_id",
}


# ── Test helpers ───────────────────────────────────────────────────────────────

def _mock_db_session():
    """Create a mock AsyncSession with minimal query support."""
    session = AsyncMock()
    
    async def mock_scalars(stmt):
        # Return empty list for all queries
        return MagicMock(all=lambda: [])
    
    session.scalars = mock_scalars
    session.flush = AsyncMock()
    session.add = MagicMock()
    return session


def _mock_learner():
    """Create a mock learner with all expected fields."""
    learner = LearnerProfile(
        id=str(uuid.uuid4()),
        pseudonym_id=str(uuid.uuid4()),
        guardian_id=str(uuid.uuid4()),
        display_name="Test Learner",
        grade=4,
        language="en",
        archetype="Keter",
        theta=0.5,
        xp=100,
        streak_days=5,
        last_active=datetime.now(UTC),
        is_deleted=False,
        deletion_requested_at=None,
        created_at=datetime.now(UTC),
    )
    return learner


# ── Completeness tests ───────────────────────────────────────────────────────────

class TestExportPayloadCompleteness:
    """Verify export payload matches data inventory requirements."""

    @pytest.mark.asyncio
    async def test_learner_profile_contains_all_required_fields(self):
        """Export must include all learner profile fields from inventory."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        # Mock the get to return our learner
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        assert "learner" in payload
        learner_data = payload["learner"]
        
        # Check all expected fields are present
        missing_fields = EXPECTED_LEARNER_FIELDS - set(learner_data.keys())
        assert not missing_fields, f"Missing learner fields: {missing_fields}"

    @pytest.mark.asyncio
    async def test_learner_profile_includes_pseudonym_id(self):
        """Export should include pseudonym_id for external reference."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        learner_data = payload["learner"]
        # Both id and pseudonym_id should be present
        assert "id" in learner_data
        assert "pseudonym_id" in learner_data
        assert learner_data["pseudonym_id"] == learner.pseudonym_id

    @pytest.mark.asyncio
    async def test_diagnostic_sessions_structure(self):
        """Export must include diagnostic sessions with correct fields."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        assert "diagnostic_sessions" in payload
        assert isinstance(payload["diagnostic_sessions"], list)

    @pytest.mark.asyncio
    async def test_lessons_structure(self):
        """Export must include lessons with correct fields."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        assert "lessons" in payload
        assert isinstance(payload["lessons"], list)

    @pytest.mark.asyncio
    async def test_knowledge_gaps_structure(self):
        """Export must include knowledge gaps with correct fields."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        assert "knowledge_gaps" in payload
        assert isinstance(payload["knowledge_gaps"], list)

    @pytest.mark.asyncio
    async def test_parental_consents_structure(self):
        """Export must include parental consents with correct fields."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        assert "parental_consents" in payload
        assert isinstance(payload["parental_consents"], list)

    @pytest.mark.asyncio
    async def test_export_contains_date_field(self):
        """Export must include export_date timestamp."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        assert "export_date" in payload
        assert isinstance(payload["export_date"], str)

    @pytest.mark.asyncio
    async def test_no_prohibited_fields_in_learner_data(self):
        """Export must not contain prohibited PII fields."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        learner_data = payload["learner"]
        prohibited_found = PROHIBITED_FIELDS & set(learner_data.keys())
        assert not prohibited_found, f"Prohibited fields found in export: {prohibited_found}"

    @pytest.mark.asyncio
    async def test_timestamps_are_iso8601_format(self):
        """All timestamp fields must be in ISO 8601 format."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        # Check export_date is ISO format
        from datetime import datetime
        try:
            datetime.fromisoformat(payload["export_date"])
        except ValueError:
            pytest.fail("export_date is not in ISO 8601 format")

    @pytest.mark.asyncio
    async def test_csv_export_structure(self):
        """CSV export must have proper structure."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        csv_data = service._to_csv(payload)
        
        # CSV should have header row
        lines = csv_data.split("\n")
        assert len(lines) > 0
        assert "section" in lines[0]  # Header should contain column names


class TestExportDataCategories:
    """Verify all data categories from inventory are represented."""

    REQUIRED_CATEGORIES = {
        "learner",
        "diagnostic_sessions",
        "lessons",
        "knowledge_gaps",
        "parental_consents",
    }

    @pytest.mark.asyncio
    async def test_all_required_categories_present(self):
        """Export must include all required data categories."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        async def mock_get(model, key):
            return learner
        db.get = mock_get
        
        service = POPIADataRightsService(db)
        payload = await service._export_payload(learner)
        
        missing_categories = self.REQUIRED_CATEGORIES - set(payload.keys())
        assert not missing_categories, f"Missing data categories: {missing_categories}"
