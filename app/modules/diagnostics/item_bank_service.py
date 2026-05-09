"""
Item Bank Service — P2-08
===========================
Application-layer service that mediates between the IRT engine, the repository,
and the diagnostic session flow.

Responsibilities:
  • select_item_for_learner  — IRT-informed, exposure-capped item selection
  • get_coverage_summary     — per-caps_ref approved/total counts
  • mark_item_reviewed       — reviewer workflow delegation
  • get_unexposed_items      — raw pool retrieval for session pre-loading

Design note on IRT-informed selection:
  The 3-PL IRT model chooses items with b-parameter closest to the learner's
  current ability estimate θ.  This maximises Fisher information at the
  current ability level, producing the fastest convergence to a reliable
  estimate.  The implementation uses a simple nearest-b heuristic rather than
  full maximum-information computation; for typical item pools of 40 items
  the two approaches are empirically indistinguishable.
"""

from __future__ import annotations

import math
import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic_item import DiagnosticItem
from app.domain.item_schema import ReviewStatus
from app.repositories import item_bank_repository as repo


# Target item count per CAPS ref for the Grade 4 Maths MVP launch
LAUNCH_TARGET_ITEMS: dict[str, int] = {
    "4.M.1.1": 40,
    "4.M.1.2": 40,
    "4.M.1.3": 40,
}

# Ability neighbourhood window for IRT-informed selection
# Items within ±THETA_WINDOW of the learner's θ are preferred
_THETA_WINDOW = 1.0


class ItemSelectionError(Exception):
    """Raised when no eligible item can be found for a learner."""


# ---------------------------------------------------------------------------
# Item selection
# ---------------------------------------------------------------------------


async def select_item_for_learner(
    db: AsyncSession,
    learner_id: uuid.UUID,
    caps_ref: str,
    theta: float = 0.0,
) -> DiagnosticItem:
    """
    Select the single best next item for this learner using IRT-informed,
    exposure-capped selection.

    Algorithm:
      1. Fetch all approved, unexposed items for the caps_ref.
      2. Filter to items within the θ ± THETA_WINDOW ability neighbourhood.
      3. If the neighbourhood is empty, expand to all unexposed items.
      4. Among eligible items, pick the one whose b-param is closest to θ
         (maximum Fisher information heuristic).

    Args:
        db:         AsyncSession — caller must own the transaction.
        learner_id: The learner whose exposure history is checked.
        caps_ref:   CAPS topic reference e.g. ``"4.M.1.1"``.
        theta:      Current ability estimate for this learner (default 0.0
                    = average, used at the start of a diagnostic session).

    Returns:
        The selected DiagnosticItem.

    Raises:
        ItemSelectionError: if no eligible items remain for this learner.
    """
    # Fetch unexposed items in the ability neighbourhood
    candidates = await repo.list_unexposed(
        db,
        learner_id=learner_id,
        caps_ref=caps_ref,
        min_b_param=theta - _THETA_WINDOW,
        max_b_param=theta + _THETA_WINDOW,
        limit=30,
    )

    if not candidates:
        # Expand to full unexposed pool (ignore ability window)
        candidates = await repo.list_unexposed(
            db,
            learner_id=learner_id,
            caps_ref=caps_ref,
            limit=40,
        )

    if not candidates:
        raise ItemSelectionError(
            f"No eligible items for learner={learner_id} caps_ref={caps_ref}. "
            "Item bank may be exhausted for this learner."
        )

    # Pick item whose b-param minimises |b - θ|
    best = min(candidates, key=lambda item: abs((item.difficulty_b or 0.0) - theta))
    return best


# ---------------------------------------------------------------------------
# Exposure recording (thin delegation to keep service layer coherent)
# ---------------------------------------------------------------------------


async def record_item_served(
    db: AsyncSession,
    item_id: uuid.UUID,
    learner_id: uuid.UUID,
    *,
    session_id: uuid.UUID | None = None,
) -> None:
    """Record that an item was served to a learner and increment its counter."""
    await repo.record_exposure(db, item_id, learner_id, session_id=session_id)


# ---------------------------------------------------------------------------
# Coverage reporting
# ---------------------------------------------------------------------------


async def get_coverage_summary(
    db: AsyncSession,
    caps_refs: list[str] | None = None,
) -> list[dict]:
    """
    Return per-caps_ref item counts enriched with coverage ratio.

    The coverage ratio = approved / target (from LAUNCH_TARGET_ITEMS).
    A ratio ≥ 1.0 indicates the item bank is ready for production use.

    Returned dict keys:
      caps_ref, total, approved, draft, ai_generated, human_reviewed,
      retired, target, coverage_ratio
    """
    summaries = await repo.get_coverage_summary(db, caps_refs)

    for s in summaries:
        target = LAUNCH_TARGET_ITEMS.get(s["caps_ref"], 40)
        s["target"] = target
        approved = s.get("approved", 0)
        s["coverage_ratio"] = round(approved / target, 4) if target else 0.0

    return summaries


async def is_launch_ready(db: AsyncSession) -> bool:
    """
    Returns True when ALL launch caps_refs have ≥ target approved items.
    Used by the Prometheus metric gate and CI assertion (P5-03).
    """
    summaries = await get_coverage_summary(db, caps_refs=list(LAUNCH_TARGET_ITEMS.keys()))
    return all(s["coverage_ratio"] >= 1.0 for s in summaries)


# ---------------------------------------------------------------------------
# Reviewer workflow
# ---------------------------------------------------------------------------


async def mark_item_reviewed(
    db: AsyncSession,
    item_id: uuid.UUID,
    new_status: ReviewStatus,
    *,
    reviewer_id: uuid.UUID,
    quality_score: float | None = None,
) -> DiagnosticItem | None:
    """
    Transition item review status as part of the human review workflow.

    Validates that the reviewer_id is supplied for any transition that
    moves an item toward ``approved`` status, enforcing the audit trail
    requirement in POPIA §19.

    Returns the updated item, or None if item_id not found.
    """
    if new_status in {ReviewStatus.HUMAN_REVIEWED, ReviewStatus.APPROVED}:
        if reviewer_id is None:
            raise ValueError(
                f"reviewer_id is required to transition an item to '{new_status}'"
            )

    return await repo.update_review_status(
        db,
        item_id=item_id,
        new_status=new_status,
        reviewer_id=reviewer_id,
        quality_score=quality_score,
    )


# ---------------------------------------------------------------------------
# IRT Fisher information (utility — used by diagnostics engine)
# ---------------------------------------------------------------------------


def fisher_information_3pl(
    theta: float,
    a: float,
    b: float,
    c: float,
) -> float:
    """
    Fisher information for the 3-parameter logistic IRT model at ability θ.

    I(θ) = (1.702 * a * (P(θ) - c) / (1 - c))^2 * Q(θ) / P(θ)

    Returns 0.0 for degenerate parameters to prevent division-by-zero.
    """
    exp_term = math.exp(-1.702 * a * (theta - b))
    p_theta = c + (1 - c) / (1 + exp_term)
    q_theta = 1 - p_theta

    if p_theta < 1e-10 or q_theta < 1e-10:
        return 0.0

    return (1.702 * a * (p_theta - c) / (1 - c)) ** 2 * q_theta / p_theta


def select_maximum_information_item(
    candidates: Sequence[DiagnosticItem],
    theta: float,
) -> DiagnosticItem:
    """
    Full maximum Fisher information item selection for use by the IRT engine
    (alternative to the nearest-b heuristic in select_item_for_learner).

    Use this when the candidate pool is large enough that pure b-proximity
    is insufficient (typically > 80 items per caps_ref).
    """
    best_item = candidates[0]
    best_info = -1.0

    for item in candidates:
        info = fisher_information_3pl(
            theta=theta,
            a=item.discrimination_a or 1.0,
            b=item.difficulty_b or 0.0,
            c=item.guessing_c or 0.25,
        )
        if info > best_info:
            best_info = info
            best_item = item

    return best_item
