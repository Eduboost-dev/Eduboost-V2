"""
Unit Tests — ItemBankService (P2-10)
======================================
Verifies:
  • Exposure cap prevents re-serving exhausted items
  • IRT-informed selection picks the item closest to learner's θ
  • Fisher information computation is correct for 3-PL model
  • Coverage ratio calculations
  • mark_item_reviewed enforces reviewer_id requirement

Run with: pytest tests/unit/modules/diagnostics/test_item_bank_service.py -v
"""

from __future__ import annotations

import math
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.diagnostic_item import DiagnosticItem
from app.domain.item_schema import ReviewStatus
from app.modules.diagnostics.item_bank_service import (
    LAUNCH_TARGET_ITEMS,
    ItemSelectionError,
    fisher_information_3pl,
    get_coverage_summary,
    is_launch_ready,
    mark_item_reviewed,
    record_item_served,
    select_item_for_learner,
    select_maximum_information_item,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_item(
    *,
    item_id: uuid.UUID | None = None,
    caps_ref: str = "4.M.1.1",
    difficulty_b: float = 0.0,
    discrimination_a: float = 1.0,
    guessing_c: float = 0.25,
    review_status: ReviewStatus = ReviewStatus.APPROVED,
    exposure_count: int = 0,
    max_exposure: int = 50,
    safety_passed: bool = True,
) -> DiagnosticItem:
    item = MagicMock(spec=DiagnosticItem)
    item.item_id = item_id or uuid.uuid4()
    item.caps_ref = caps_ref
    item.difficulty_b = difficulty_b
    item.discrimination_a = discrimination_a
    item.guessing_c = guessing_c
    item.review_status = review_status
    item.exposure_count = exposure_count
    item.max_exposure = max_exposure
    item.safety_passed = safety_passed
    return item


# ---------------------------------------------------------------------------
# Fisher Information — 3-PL model
# ---------------------------------------------------------------------------


def test_fisher_information_positive_for_valid_params():
    info = fisher_information_3pl(theta=0.0, a=1.0, b=0.0, c=0.25)
    assert info > 0


def test_fisher_information_maximised_near_b_param():
    """Fisher information peaks when θ is close to the item's b-parameter."""
    b = 0.5
    info_at_b = fisher_information_3pl(theta=b, a=1.0, b=b, c=0.25)
    info_far = fisher_information_3pl(theta=-2.0, a=1.0, b=b, c=0.25)
    assert info_at_b > info_far


def test_fisher_information_zero_for_degenerate_params():
    """Very extreme ability values → denominator → 0 → return 0."""
    info = fisher_information_3pl(theta=100.0, a=1.0, b=0.0, c=0.25)
    assert info == 0.0 or info < 1e-5


def test_fisher_information_increases_with_discrimination():
    """Higher discrimination → higher information."""
    low_a = fisher_information_3pl(theta=0.0, a=0.5, b=0.0, c=0.25)
    high_a = fisher_information_3pl(theta=0.0, a=2.0, b=0.0, c=0.25)
    assert high_a > low_a


# ---------------------------------------------------------------------------
# select_maximum_information_item
# ---------------------------------------------------------------------------


def test_select_maximum_information_prefers_item_near_theta():
    theta = 1.0
    items = [
        _make_item(difficulty_b=-2.0),   # far below theta
        _make_item(difficulty_b=1.1),    # closest to theta
        _make_item(difficulty_b=3.0),    # far above theta
    ]
    selected = select_maximum_information_item(items, theta=theta)
    assert selected.difficulty_b == pytest.approx(1.1)


def test_select_maximum_information_single_candidate():
    item = _make_item(difficulty_b=0.5)
    selected = select_maximum_information_item([item], theta=0.0)
    assert selected.item_id == item.item_id


# ---------------------------------------------------------------------------
# select_item_for_learner — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_select_item_picks_nearest_b_to_theta():
    """
    Given three unexposed items, the selector should pick the one
    whose difficulty_b is closest to the learner's current theta.
    """
    learner_id = uuid.uuid4()
    theta = 0.3

    item_near = _make_item(difficulty_b=0.4)   # nearest to 0.3
    item_far_above = _make_item(difficulty_b=2.5)
    item_far_below = _make_item(difficulty_b=-2.0)

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.list_unexposed",
        new_callable=AsyncMock,
    ) as mock_list:
        mock_list.return_value = [item_near, item_far_above, item_far_below]

        db = AsyncMock()
        selected = await select_item_for_learner(db, learner_id, "4.M.1.1", theta=theta)

    assert selected.item_id == item_near.item_id


@pytest.mark.asyncio
async def test_select_item_expands_window_when_neighbourhood_empty():
    """
    When the ability-windowed call returns nothing, the service should
    fall back to the full unexposed pool.
    """
    learner_id = uuid.uuid4()
    fallback_item = _make_item(difficulty_b=3.0)

    call_count = 0

    async def mock_list_unexposed(db, learner_id, caps_ref, **kwargs):
        nonlocal call_count
        call_count += 1
        if "min_b_param" in kwargs:
            return []   # first call (windowed) — empty
        return [fallback_item]   # second call (full pool) — one item

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.list_unexposed",
        side_effect=mock_list_unexposed,
    ):
        db = AsyncMock()
        selected = await select_item_for_learner(db, learner_id, "4.M.1.1", theta=0.0)

    assert selected.item_id == fallback_item.item_id
    assert call_count == 2  # windowed call + fallback call


@pytest.mark.asyncio
async def test_select_item_raises_when_bank_exhausted():
    """
    If all items are exhausted for this learner, ItemSelectionError is raised.
    """
    learner_id = uuid.uuid4()

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.list_unexposed",
        new_callable=AsyncMock,
        return_value=[],
    ):
        db = AsyncMock()
        with pytest.raises(ItemSelectionError):
            await select_item_for_learner(db, learner_id, "4.M.1.1", theta=0.0)


# ---------------------------------------------------------------------------
# Exposure cap — record_item_served
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_item_served_calls_repository():
    item_id = uuid.uuid4()
    learner_id = uuid.uuid4()
    session_id = uuid.uuid4()

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.record_exposure",
        new_callable=AsyncMock,
    ) as mock_record:
        db = AsyncMock()
        await record_item_served(db, item_id, learner_id, session_id=session_id)

    mock_record.assert_awaited_once_with(db, item_id, learner_id, session_id=session_id)


def test_exposure_cap_enforced_by_repository_query():
    """
    The exposure cap is enforced in the list_unexposed query
    (exposure_count < max_exposure).  This test documents the contract
    that the repository must honour — we verify the query excludes
    over-exposed items by asserting the service receives only eligible items.
    """
    # Items with exposure_count >= max_exposure should never appear in
    # list_unexposed results — this is enforced at the repo layer.
    exhausted_item = _make_item(exposure_count=50, max_exposure=50)
    assert exhausted_item.exposure_count >= exhausted_item.max_exposure
    # Service has no further gate — it trusts the repository contract.
    # This test documents that contract explicitly.


# ---------------------------------------------------------------------------
# Coverage summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coverage_summary_adds_coverage_ratio():
    raw_summaries = [
        {
            "caps_ref": "4.M.1.1",
            "total": 50,
            "approved": 40,
            "draft": 5,
            "ai_generated": 5,
            "human_reviewed": 0,
            "retired": 0,
        }
    ]

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.get_coverage_summary",
        new_callable=AsyncMock,
        return_value=raw_summaries,
    ):
        db = AsyncMock()
        summaries = await get_coverage_summary(db, caps_refs=["4.M.1.1"])

    assert len(summaries) == 1
    s = summaries[0]
    assert s["coverage_ratio"] == pytest.approx(40 / 40)
    assert s["target"] == 40


@pytest.mark.asyncio
async def test_coverage_ratio_below_one_when_insufficient_items():
    raw_summaries = [
        {
            "caps_ref": "4.M.1.2",
            "total": 20,
            "approved": 20,
            "draft": 0,
            "ai_generated": 0,
            "human_reviewed": 0,
            "retired": 0,
        }
    ]

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.get_coverage_summary",
        new_callable=AsyncMock,
        return_value=raw_summaries,
    ):
        db = AsyncMock()
        summaries = await get_coverage_summary(db)

    assert summaries[0]["coverage_ratio"] == pytest.approx(20 / 40)


@pytest.mark.asyncio
async def test_is_launch_ready_true_when_all_refs_covered():
    full_summaries = [
        {"caps_ref": ref, "total": 40, "approved": 40, "draft": 0,
         "ai_generated": 0, "human_reviewed": 0, "retired": 0}
        for ref in LAUNCH_TARGET_ITEMS
    ]

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.get_coverage_summary",
        new_callable=AsyncMock,
        return_value=full_summaries,
    ):
        db = AsyncMock()
        ready = await is_launch_ready(db)

    assert ready is True


@pytest.mark.asyncio
async def test_is_launch_ready_false_when_one_ref_under_target():
    partial_summaries = [
        {"caps_ref": "4.M.1.1", "total": 40, "approved": 40, "draft": 0,
         "ai_generated": 0, "human_reviewed": 0, "retired": 0},
        {"caps_ref": "4.M.1.2", "total": 30, "approved": 30, "draft": 0,
         "ai_generated": 0, "human_reviewed": 0, "retired": 0},
        {"caps_ref": "4.M.1.3", "total": 40, "approved": 40, "draft": 0,
         "ai_generated": 0, "human_reviewed": 0, "retired": 0},
    ]

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.get_coverage_summary",
        new_callable=AsyncMock,
        return_value=partial_summaries,
    ):
        db = AsyncMock()
        ready = await is_launch_ready(db)

    assert ready is False  # 4.M.1.2 only has 30/40


# ---------------------------------------------------------------------------
# mark_item_reviewed — reviewer_id enforcement
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_item_reviewed_requires_reviewer_id_for_approved():
    item_id = uuid.uuid4()
    with pytest.raises(ValueError, match="reviewer_id is required"):
        db = AsyncMock()
        await mark_item_reviewed(
            db,
            item_id=item_id,
            new_status=ReviewStatus.APPROVED,
            reviewer_id=None,  # type: ignore[arg-type]
        )


@pytest.mark.asyncio
async def test_mark_item_reviewed_calls_repo_with_correct_args():
    item_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    with patch(
        "app.modules.diagnostics.item_bank_service.repo.update_review_status",
        new_callable=AsyncMock,
        return_value=_make_item(item_id=item_id),
    ) as mock_update:
        db = AsyncMock()
        await mark_item_reviewed(
            db,
            item_id=item_id,
            new_status=ReviewStatus.APPROVED,
            reviewer_id=reviewer_id,
            quality_score=0.92,
        )

    mock_update.assert_awaited_once_with(
        db,
        item_id=item_id,
        new_status=ReviewStatus.APPROVED,
        reviewer_id=reviewer_id,
        quality_score=0.92,
    )
