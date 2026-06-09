"""
arq Worker Job — Practice Session Cleanup (Phase 2.2)
======================================================
Periodically deletes expired practice sessions to maintain database hygiene.

Register this module in your arq WorkerSettings.functions list:

Example WorkerSettings (app/core/arq_worker.py):
    from app.jobs.practice_session_cleanup_job import run_practice_session_cleanup

    class WorkerSettings:
        functions = [run_practice_session_cleanup]
        cron_jobs = [
            cron(run_practice_session_cleanup, hour=3, minute=0)  # 3 AM daily
        ]
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arq.connections import ArqRedis  # type: ignore[import]

logger = logging.getLogger(__name__)


async def run_practice_session_cleanup(ctx: dict) -> dict:
    """
    arq-compatible daily job for deleting expired practice sessions.

    ``ctx`` is populated by arq with the worker context dict.
    We expect ``ctx["db_session_factory"]`` to be injected at worker startup.
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.repositories.practice_session_repository import PracticeSessionRepository

    session_factory = ctx.get("db_session_factory")

    if session_factory is None:
        logger.error(
            "practice_session_cleanup_job_misconfigured",
            extra={"missing": ["db_session_factory"]},
        )
        return {"error": "Worker context missing db_session_factory"}

    async with AsyncSession(session_factory) as db:
        repo = PracticeSessionRepository(db)
        deleted_count = await repo.delete_expired()
        logger.info(
            "practice_session_cleanup_completed",
            extra={"deleted_count": deleted_count},
        )
        return {"deleted_count": deleted_count}
