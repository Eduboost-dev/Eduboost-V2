"""
Item Bank Repository — P2-01 / P3 Refactor
==========================================
Persistence layer for diagnostic items and exposure tracking.
All DB I/O is async; callers must run inside an AsyncSession context.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.domain.item_schema import ReviewStatus
from app.models.item_exposure import ItemExposure


class ItemBankRepository:
    """
    Class-based repository for diagnostic items.
    Aligns with Phase 3 integration testing and service patterns.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ─── Read operations ─────────────────────────────────────────────────────

    async def get_item(self, item_id: uuid.UUID) -> Optional[DiagnosticItem]:
        """Return a single DiagnosticItem by primary key, or None."""
        result = await self.db.execute(
            select(DiagnosticItem).where(DiagnosticItem.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_by_caps_ref(
        self,
        caps_ref: str,
        *,
        review_status: Optional[ReviewStatus] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> Sequence[DiagnosticItem]:
        """Return items for a CAPS reference code."""
        stmt = (
            select(DiagnosticItem)
            .where(DiagnosticItem.caps_ref == caps_ref)
            .order_by(DiagnosticItem.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        if review_status is not None:
            # Handle both Domain Enum and Model Enum for robustness
            status_val = review_status.value if hasattr(review_status, "value") else review_status
            stmt = stmt.where(DiagnosticItem.review_status == status_val)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_unexposed_items(
        self,
        learner_id: uuid.UUID,
        caps_ref: str,
        *,
        max_b_param: Optional[float] = None,
        min_b_param: Optional[float] = None,
        limit: int = 20,
    ) -> Sequence[DiagnosticItem]:
        """
        Return approved items for *caps_ref* that this learner has not yet seen.
        Renamed from list_unexposed to match Phase 3 test expectations.
        """
        seen_subq = (
            select(ItemExposure.item_id)
            .where(ItemExposure.learner_id == learner_id)
            .scalar_subquery()
        )

        stmt = (
            select(DiagnosticItem)
            .where(
                DiagnosticItem.caps_ref == caps_ref,
                DiagnosticItem.review_status == ReviewStatusEnum.APPROVED,
                DiagnosticItem.safety_passed.is_(True),
                DiagnosticItem.exposure_count < DiagnosticItem.max_exposure,
                DiagnosticItem.item_id.not_in(seen_subq),
            )
            .order_by(DiagnosticItem.difficulty_b.asc())
            .limit(limit)
        )

        if min_b_param is not None:
            stmt = stmt.where(DiagnosticItem.difficulty_b >= min_b_param)
        if max_b_param is not None:
            stmt = stmt.where(DiagnosticItem.difficulty_b <= max_b_param)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_coverage_summary(
        self,
        caps_refs: Optional[list[str]] = None,
    ) -> dict[str, dict]:
        """
        Return per-caps_ref item counts. 
        Returns a dict keyed by caps_ref for easier service-layer processing.
        """
        stmt = select(
            DiagnosticItem.caps_ref,
            DiagnosticItem.review_status,
            func.count(DiagnosticItem.item_id).label("cnt"),
        ).group_by(DiagnosticItem.caps_ref, DiagnosticItem.review_status)

        if caps_refs:
            stmt = stmt.where(DiagnosticItem.caps_ref.in_(caps_refs))

        result = await self.db.execute(stmt)
        rows = result.all()

        summary: dict[str, dict] = {}
        for caps_ref, status, cnt in rows:
            if caps_ref not in summary:
                summary[caps_ref] = {
                    "caps_ref": caps_ref,
                    "total": 0,
                    "approved": 0,
                    "draft": 0,
                    "ai_generated": 0,
                    "human_reviewed": 0,
                    "retired": 0,
                }
            
            # Map status enum value to dict key
            status_key = status.value if hasattr(status, "value") else str(status)
            summary[caps_ref]["total"] += cnt
            if status_key in summary[caps_ref]:
                summary[caps_ref][status_key] += cnt

        return summary

    # ─── Write operations ────────────────────────────────────────────────────

    async def record_exposure(
        self,
        item_id: uuid.UUID,
        learner_id: uuid.UUID,
        *,
        session_id: Optional[uuid.UUID] = None,
    ) -> ItemExposure:
        """Persist an exposure event and atomically increment the item's counter."""
        exposure = ItemExposure(
            exposure_id=uuid.uuid4(),
            item_id=item_id,
            learner_id=learner_id,
            session_id=session_id,
            served_at=datetime.now(tz=timezone.utc),
        )
        self.db.add(exposure)

        await self.db.execute(
            update(DiagnosticItem)
            .where(DiagnosticItem.item_id == item_id)
            .values(exposure_count=DiagnosticItem.exposure_count + 1)
        )

        await self.db.flush()
        return exposure

    async def update_review_status(
        self,
        item_id: uuid.UUID,
        new_status: str,
        *,
        reviewer_id: Optional[uuid.UUID] = None,
        quality_score: Optional[float] = None,
    ) -> Optional[DiagnosticItem]:
        """Transition an item's review workflow status."""
        item = await self.get_item(item_id)
        if item is None:
            return None

        # Convert string status to enum if needed
        if isinstance(new_status, str):
            item.review_status = ReviewStatusEnum(new_status)
        else:
            item.review_status = new_status

        if reviewer_id is not None:
            item.reviewer_id = reviewer_id
            item.reviewed_at = datetime.now(tz=timezone.utc)
        if quality_score is not None:
            item.quality_score = quality_score

        await self.db.flush()
        return item

    async def upsert(self, data: dict) -> DiagnosticItem:
        """
        Idempotent upsert from a dictionary. 
        Used by seeder and generator pipelines.
        """
        item_id = uuid.UUID(data["item_id"]) if isinstance(data["item_id"], str) else data["item_id"]
        
        existing = await self.get_item(item_id)
        if existing:
            # Update fields
            for key, value in data.items():
                if key in ("item_id", "created_at"):
                    continue
                if hasattr(existing, key):
                    # Handle Enum conversion
                    if key == "review_status" and isinstance(value, str):
                        value = ReviewStatusEnum(value)
                    elif key == "item_type" and isinstance(value, str):
                        value = DiagnosticItem.__table__.columns["item_type"].type.python_type(value)
                    # Add more conversions as needed or use a more robust mapper
                    setattr(existing, key, value)
            await self.db.flush()
            return existing
        
        # Create new
        new_item = DiagnosticItem(**data)
        # Ensure UUIDs are objects
        if isinstance(new_item.item_id, str):
            new_item.item_id = uuid.UUID(new_item.item_id)
        if data.get("reviewer_id") and isinstance(data["reviewer_id"], str):
            new_item.reviewer_id = uuid.UUID(data["reviewer_id"])
            
        self.db.add(new_item)
        await self.db.flush()
        return new_item
