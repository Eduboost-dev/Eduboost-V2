"""Audit routes for EduBoost V2."""

from fastapi import APIRouter, Depends
from app.core.envelope_route import EnvelopedRoute
from app.core.security import get_current_user

from app.services.audit_service import AuditService

router = APIRouter(route_class=EnvelopedRoute, prefix="/audit", tags=["V2 Audit"])


@router.get("", dependencies=[Depends(get_current_user)])
async def get_audit_feed(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)


@router.get("/feed", dependencies=[Depends(get_current_user)])
async def get_audit_feed_alias(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)
