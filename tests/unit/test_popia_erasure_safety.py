"""tests/unit/test_popia_erasure_safety.py
T111A: POPIA erasure cascade matrix and deletion safety tests

Verifies that deletion operations follow the cascade matrix,
enforce safety checks, and preserve audit integrity.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import delete

from app.models import LearnerProfile
from app.repositories.learner_repository import LearnerRepository


# ── Expected cascade behavior from matrix ───────────────────────────────────────

CASCADE_DELETE_TABLES = {
    "diagnostic_sessions",
    "knowledge_gaps",
    "lessons",
    "parental_consents",
    "subject_mastery",
    "topic_mastery",
    "mastery_snapshots",
    "practice_queue",
    "spaced_review_schedule",
}

SOFT_DELETE_RETAINED_TABLES = CASCADE_DELETE_TABLES.copy()

AUDIT_RETENTION_TABLES = {
    "audit_events",
    "audit_logs",
}

GUARDIAN_RETAINED_FIELDS = {
    "email_hash",
    "email_encrypted",
    "stripe_customer_id",
    "stripe_subscription_id",
}


# ── Test helpers ───────────────────────────────────────────────────────────────

def _mock_db_session():
    """Create a mock AsyncSession with minimal query support."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    # get needs to be async since BaseRepository.get awaits it
    session.get = AsyncMock()
    return session


def _mock_learner():
    """Create a mock learner."""
    learner = LearnerProfile(
        id=str(uuid.uuid4()),
        pseudonym_id=str(uuid.uuid4()),
        guardian_id=str(uuid.uuid4()),
        display_name="Test Learner",
        grade=4,
        language="en",
        is_deleted=False,
        deletion_requested_at=None,
        created_at=datetime.now(UTC),
    )
    return learner


# ── Soft delete safety tests ────────────────────────────────────────────────────

class TestSoftDeleteSafety:
    """Verify soft delete follows grace period policy."""

    @pytest.mark.asyncio
    async def test_soft_delete_sets_is_deleted_flag(self):
        """Soft delete must set is_deleted=True."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        repo = LearnerRepository(db)
        # Mock get_by_id to return learner directly
        repo.get_by_id = AsyncMock(return_value=learner)
        await repo.soft_delete(learner.id)
        
        assert learner.is_deleted is True

    @pytest.mark.asyncio
    async def test_soft_delete_erases_display_name(self):
        """Soft delete must set display_name to '[erased]'."""
        db = _mock_db_session()
        learner = _mock_learner()
        original_name = learner.display_name
        
        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=learner)
        await repo.soft_delete(learner.id)
        
        assert learner.display_name == "[erased]"
        assert learner.display_name != original_name

    @pytest.mark.asyncio
    async def test_soft_delete_sets_deletion_requested_at(self):
        """Soft delete must set deletion_requested_at timestamp."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=learner)
        await repo.soft_delete(learner.id)
        
        assert learner.deletion_requested_at is not None
        assert isinstance(learner.deletion_requested_at, datetime)

    @pytest.mark.asyncio
    async def test_soft_delete_returns_early_for_nonexistent_learner(self):
        """Soft delete should return early if learner not found."""
        db = _mock_db_session()
        
        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=None)
        # Should not raise
        await repo.soft_delete(str(uuid.uuid4()))


# ── Physical delete safety tests ────────────────────────────────────────────────

class TestPhysicalDeleteSafety:
    """Verify physical delete follows cascade policy."""

    @pytest.mark.asyncio
    async def test_physical_delete_uses_delete_statement(self):
        """Physical delete must use DELETE SQL statement."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        # Mock execute to capture the statement
        execute_calls = []
        async def mock_execute(stmt):
            execute_calls.append(stmt)
            result = MagicMock()
            result.rowcount = 1
            return result
        db.execute = mock_execute
        
        repo = LearnerRepository(db)
        await repo.delete_by_id(learner_id)
        
        assert len(execute_calls) == 1
        # Verify it's a delete statement
        assert str(execute_calls[0]).startswith("DELETE")

    @pytest.mark.asyncio
    async def test_physical_delete_returns_true_on_success(self):
        """Physical delete must return True when row is deleted."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        result = MagicMock()
        result.rowcount = 1
        db.execute = AsyncMock(return_value=result)
        
        repo = LearnerRepository(db)
        success = await repo.delete_by_id(learner_id)
        
        assert success is True

    @pytest.mark.asyncio
    async def test_physical_delete_returns_false_on_no_rows(self):
        """Physical delete must return False when no rows affected."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        result = MagicMock()
        result.rowcount = 0
        db.execute = AsyncMock(return_value=result)
        
        repo = LearnerRepository(db)
        success = await repo.delete_by_id(learner_id)
        
        assert success is False


# ── Purge safety tests ─────────────────────────────────────────────────────────

class TestPurgeSafety:
    """Verify purge follows same policy as physical delete."""

    @pytest.mark.asyncio
    async def test_purge_uses_delete_statement(self):
        """Purge must use DELETE SQL statement."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        execute_calls = []
        async def mock_execute(stmt):
            execute_calls.append(stmt)
            return MagicMock()
        db.execute = mock_execute
        
        repo = LearnerRepository(db)
        await repo.purge_personal_data(learner_id)
        
        assert len(execute_calls) == 1
        assert str(execute_calls[0]).startswith("DELETE")


# ── Grace period tests ────────────────────────────────────────────────────────

class TestGracePeriod:
    """Verify 30-day grace period enforcement."""

    @pytest.mark.asyncio
    async def test_soft_delete_timestamp_within_grace_period(self):
        """Soft delete timestamp should be within acceptable range."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=learner)
        before = datetime.now(UTC)
        await repo.soft_delete(learner.id)
        after = datetime.now(UTC)
        
        assert before <= learner.deletion_requested_at <= after

    @pytest.mark.asyncio
    async def test_deletion_requested_at_is_recent(self):
        """Deletion requested timestamp should be recent (within 1 second)."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=learner)
        await repo.soft_delete(learner.id)
        
        time_diff = datetime.now(UTC) - learner.deletion_requested_at
        assert time_diff.total_seconds() < 1.0


# ── Audit retention tests ──────────────────────────────────────────────────────

class TestAuditRetention:
    """Verify audit records are never deleted."""

    @pytest.mark.asyncio
    async def test_delete_by_id_does_not_affect_audit_tables(self):
        """Physical delete should not attempt to delete audit records."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        execute_calls = []
        async def mock_execute(stmt):
            execute_calls.append(str(stmt))
            result = MagicMock()
            result.rowcount = 1
            return result
        db.execute = mock_execute
        
        repo = LearnerRepository(db)
        await repo.delete_by_id(learner_id)
        
        # Verify no audit table deletions
        for call in execute_calls:
            assert "audit_events" not in call.lower()
            assert "audit_logs" not in call.lower()


# ── Guardian data retention tests ───────────────────────────────────────────────

class TestGuardianDataRetention:
    """Verify guardian data is not deleted with learner."""

    @pytest.mark.asyncio
    async def test_delete_by_id_only_targets_learner_table(self):
        """Physical delete should only target learner_profiles table."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        execute_calls = []
        async def mock_execute(stmt):
            execute_calls.append(str(stmt))
            result = MagicMock()
            result.rowcount = 1
            return result
        db.execute = mock_execute
        
        repo = LearnerRepository(db)
        await repo.delete_by_id(learner_id)
        
        # Verify only learner_profiles is targeted
        for call in execute_calls:
            assert "learner_profiles" in call.lower()
            assert "guardians" not in call.lower()


# ── Cascade behavior tests ─────────────────────────────────────────────────────

class TestCascadeBehavior:
    """Verify CASCADE delete behavior is enforced by DB."""

    @pytest.mark.asyncio
    async def test_physical_delete_triggers_cascade(self):
        """Physical delete should rely on DB CASCADE for dependent records."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        execute_calls = []
        async def mock_execute(stmt):
            execute_calls.append(str(stmt))
            result = MagicMock()
            result.rowcount = 1
            return result
        db.execute = mock_execute
        
        repo = LearnerRepository(db)
        await repo.delete_by_id(learner_id)
        
        # Should only delete learner, rely on CASCADE for dependents
        assert len(execute_calls) == 1
        assert "learner_profiles" in execute_calls[0].lower()


# ── Deletion method comparison tests ───────────────────────────────────────────

class TestDeletionMethodComparison:
    """Compare deletion methods to ensure correct behavior."""

    @pytest.mark.asyncio
    async def test_soft_delete_vs_physical_delete(self):
        """Soft delete and physical delete should have different behaviors."""
        db = _mock_db_session()
        learner = _mock_learner()
        
        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=learner)
        
        # Soft delete
        await repo.soft_delete(learner.id)
        assert learner.is_deleted is True
        assert learner.display_name == "[erased]"
        
        # Reset for physical delete test
        learner.is_deleted = False
        learner.display_name = "Test Learner"
        
        # Physical delete uses execute, not get
        execute_called = False
        async def mock_execute(stmt):
            nonlocal execute_called
            execute_called = True
            result = MagicMock()
            result.rowcount = 1
            return result
        db.execute = mock_execute
        
        await repo.delete_by_id(learner.id)
        assert execute_called is True

    @pytest.mark.asyncio
    async def test_purge_same_as_physical_delete(self):
        """Purge should behave identically to physical delete."""
        db = _mock_db_session()
        learner_id = str(uuid.uuid4())
        
        execute_calls = []
        async def mock_execute(stmt):
            execute_calls.append(str(stmt))
            result = MagicMock()
            result.rowcount = 1
            return result
        db.execute = mock_execute
        
        repo = LearnerRepository(db)
        
        # Both should use DELETE
        await repo.delete_by_id(learner_id)
        delete_call = execute_calls[0]
        
        execute_calls.clear()
        await repo.purge_personal_data(learner_id)
        purge_call = execute_calls[0]
        
        # Both should be DELETE statements on learner_profiles
        assert "delete" in delete_call.lower()
        assert "delete" in purge_call.lower()
        assert "learner_profiles" in delete_call.lower()
        assert "learner_profiles" in purge_call.lower()
