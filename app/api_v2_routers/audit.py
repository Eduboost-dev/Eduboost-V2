"""Audit routes for EduBoost V2."""

from fastapi import APIRouter

from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["V2 Audit"])


@router.get("")
async def get_audit_feed(limit: int = 20, cursor: str | None = None):
    """Return recent audit events.

    When `cursor` is not provided this remains backwards-compatible and
    returns a simple list. When `cursor` is supplied, a paginated response
    with `events` and `next_cursor` is returned.
    """
    result = await AuditService().get_recent_events(limit=limit, cursor=cursor)
    return result


@router.get("/feed")
async def get_audit_feed_alias(limit: int = 20, cursor: str | None = None):
    return await AuditService().get_recent_events(limit=limit, cursor=cursor)
