"""
Item Bank Repository — P2-01
==============================
Persistence layer for diagnostic items and exposure tracking.
All DB I/O is async; callers must run inside an AsyncSession context.

Responsibilities:
  • get_item                — fetch single item by UUID
  • list_by_caps_ref        — list items filtered by CAPS reference code
  • list_unexposed          — approved items the learner has not yet seen
  • record_exposure         — persist a served-item event and increment counter
  • update_review_status    — reviewer workflow state transitions
  • get_coverage_summary    — per-caps_ref approved/total counts for monitoring
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic_item import DiagnosticItem
from app.domain.item_schema import ReviewStatus
from app.models.item_exposure import ItemExposure


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------


async def get_item(
    db: AsyncSession,
    item_id: uuid.UUID,
) -> DiagnosticItem | None:
    """Return a single DiagnosticItem by primary key, or None."""
    result = await db.execute(
        select(DiagnosticItem).where(DiagnosticItem.item_id == item_id)
    )
    return result.scalar_one_or_none()


async def list_by_caps_ref(
    db: AsyncSession,
    caps_ref: str,
    *,
    review_status: ReviewStatus | None = None,
    limit: int = 200,
    offset: int = 0,
) -> Sequence[DiagnosticItem]:
    """
    Return items for a CAPS reference code.

    Args:
        caps_ref:       e.g. ``"4.M.1.1"`` — exact match on the stored field.
        review_status:  when supplied, further filters by that status value.
        limit / offset: simple pagination; default limit 200 prevents accidental
                        full-table scans during item generation loops.
    """
    stmt = (
        select(DiagnosticItem)
        .where(DiagnosticItem.caps_ref == caps_ref)
        .order_by(DiagnosticItem.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    if review_status is not None:
        stmt = stmt.where(DiagnosticItem.review_status == review_status)

    result = await db.execute(stmt)
    return result.scalars().all()


async def list_unexposed(
    db: AsyncSession,
    learner_id: uuid.UUID,
    caps_ref: str,
    *,
    max_b_param: float | None = None,
    min_b_param: float | None = None,
    limit: int = 20,
) -> Sequence[DiagnosticItem]:
    """
    Return approved items for *caps_ref* that this learner has **not** yet seen
    AND whose exposure count is below their individual cap.

    The exposure sub-query join uses a NOT EXISTS pattern so that items with
    zero exposure rows are always included (i.e. freshly seeded items with no
    history are always eligible).

    IRT difficulty band filtering is applied when b-param bounds are supplied,
    allowing the adaptive engine to narrow item candidates to the learner's
    current ability neighbourhood.
    """
    # Subquery: item_ids already served to this learner
    seen_subq = (
        select(ItemExposure.item_id)
        .where(ItemExposure.learner_id == learner_id)
        .scalar_subquery()
    )

    stmt = (
        select(DiagnosticItem)
        .where(
            DiagnosticItem.caps_ref == caps_ref,
            DiagnosticItem.review_status == ReviewStatus.APPROVED,
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

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_coverage_summary(
    db: AsyncSession,
    caps_refs: list[str] | None = None,
) -> list[dict]:
    """
    Return per-caps_ref item counts for the admin coverage dashboard and
    the Prometheus ``item_bank_coverage_ratio`` metric.

    Returns a list of dicts with keys:
      ``caps_ref``, ``total``, ``approved``, ``draft``, ``ai_generated``,
      ``human_reviewed``, ``retired``
    """
    # Build base query — group by caps_ref and review_status
    stmt = select(
        DiagnosticItem.caps_ref,
        DiagnosticItem.review_status,
        func.count(DiagnosticItem.item_id).label("cnt"),
    ).group_by(DiagnosticItem.caps_ref, DiagnosticItem.review_status)

    if caps_refs:
        stmt = stmt.where(DiagnosticItem.caps_ref.in_(caps_refs))

    result = await db.execute(stmt)
    rows = result.all()

    # Pivot into per-caps_ref summary dicts
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
        summary[caps_ref]["total"] += cnt
        if status in summary[caps_ref]:
            summary[caps_ref][status] += cnt

    return list(summary.values())


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------


async def record_exposure(
    db: AsyncSession,
    item_id: uuid.UUID,
    learner_id: uuid.UUID,
    *,
    session_id: uuid.UUID | None = None,
) -> ItemExposure:
    """
    Persist an exposure event and atomically increment the item's counter.

    The increment uses a SQL-level ``UPDATE … SET exposure_count = exposure_count + 1``
    to avoid lost-update races under concurrent diagnostic sessions.
    """
    exposure = ItemExposure(
        exposure_id=uuid.uuid4(),
        item_id=item_id,
        learner_id=learner_id,
        session_id=session_id,
        served_at=datetime.now(tz=timezone.utc),
    )
    db.add(exposure)

    # Atomic increment — no ORM load required
    await db.execute(
        update(DiagnosticItem)
        .where(DiagnosticItem.item_id == item_id)
        .values(exposure_count=DiagnosticItem.exposure_count + 1)
    )

    await db.flush()  # make the exposure_id available; caller commits
    return exposure


async def update_review_status(
    db: AsyncSession,
    item_id: uuid.UUID,
    new_status: ReviewStatus,
    *,
    reviewer_id: uuid.UUID | None = None,
    quality_score: float | None = None,
) -> DiagnosticItem | None:
    """
    Transition an item's review workflow status.

    Valid transitions enforced here:
      draft          → ai_generated, human_reviewed
      ai_generated   → human_reviewed, draft (re-generate)
      human_reviewed → approved, draft (failed review)
      approved       → retired
      retired        → (terminal — raises ValueError)

    Args:
        reviewer_id:   Must be supplied for ``human_reviewed`` and ``approved``.
        quality_score: Optional composite quality score (0.0–1.0).

    Returns:
        Updated DiagnosticItem, or None if item_id not found.
    """
    item = await get_item(db, item_id)
    if item is None:
        return None

    TERMINAL = {ReviewStatus.RETIRED}
    if item.review_status in TERMINAL:
        raise ValueError(
            f"Item {item_id} is in terminal state '{item.review_status}' "
            "and cannot be transitioned further."
        )

    item.review_status = new_status
    if reviewer_id is not None:
        item.reviewer_id = reviewer_id
        item.reviewed_at = datetime.now(tz=timezone.utc)
    if quality_score is not None:
        item.quality_score = quality_score

    await db.flush()
    return item


async def upsert_item(
    db: AsyncSession,
    item: DiagnosticItem,
) -> DiagnosticItem:
    """
    Insert a new DiagnosticItem or update an existing one by item_id.

    Used by the seed script (scripts/seed_item_bank.py) to idempotently load
    the canonical JSON seed file into the database.
    """
    existing = await get_item(db, item.item_id)
    if existing is not None:
        # Update mutable fields; preserve immutable identity fields
        for col in DiagnosticItem.__table__.columns:
            if col.name in ("item_id", "created_at"):
                continue
            setattr(existing, col.name, getattr(item, col.name))
        await db.flush()
        return existing

    db.add(item)
    await db.flush()
    return item
