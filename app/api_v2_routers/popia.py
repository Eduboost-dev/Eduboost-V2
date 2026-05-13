from __future__ import annotations
from app.repositories.learner_repository import LearnerRepository
from app.security.dependencies import require_learner_read_for_current_user, require_learner_write_for_current_user
from app.security.dependencies import require_active_consent_for_current_user
from typing import Any
"""
app/api_v2_routers/popia.py
POPIA endpoints: consent lifecycle (§4.1) and data-subject rights (§4.3).
All learner-data routes use the require_active_consent dependency (§4.2).
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.consent_gate import ActiveConsent, require_active_consent
from app.domain.consent import ConsentRecord
from app.domain.data_subject_rights import (
    CorrectionRequest,
    DataExportRequest,
    ErasureRequest,
    RestrictionRequest,
)
from app.services.consent_service import ConsentService
from app.services.data_subject_rights_service import DataSubjectRightsService

router = APIRouter(prefix="/popia", tags=["popia"])


async def get_consent_service_for_router() -> ConsentService:
    # Runtime DI placeholder. Concrete service wiring should override this dependency.
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Consent service dependency is not configured",
    )


async def get_data_subject_rights_service_for_router() -> DataSubjectRightsService:
    # Runtime DI placeholder for data-subject rights service.
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Data-subject rights service dependency is not configured",
    )


# ---------------------------------------------------------------------------
# Request/response schemas
# ---------------------------------------------------------------------------

class ConsentGrantRequest(BaseModel):
    learner_id: uuid.UUID
    guardian_id: uuid.UUID
    privacy_notice_version: str


class ConsentDenyRequest(BaseModel):
    learner_id: uuid.UUID
    guardian_id: uuid.UUID
    privacy_notice_version: str
    reason: Optional[str] = None


class ConsentWithdrawRequest(BaseModel):
    learner_id: uuid.UUID


class ConsentRenewRequest(BaseModel):
    learner_id: uuid.UUID
    privacy_notice_version: str


class ExportRequestBody(BaseModel):
    learner_id: uuid.UUID
    format: str = "json"


class ErasureRequestBody(BaseModel):
    learner_id: uuid.UUID


class ErasureApproveBody(BaseModel):
    review_notes: Optional[str] = None


class CorrectionRequestBody(BaseModel):
    learner_id: uuid.UUID
    field_name: str
    new_value: str
    old_value: Optional[str] = None


class RestrictionRequestBody(BaseModel):
    learner_id: uuid.UUID
    reason: str


# ---------------------------------------------------------------------------
# §4.1 Consent lifecycle
# ---------------------------------------------------------------------------

@router.post("/consent/grant", response_model=ConsentRecord)
async def grant_consent(
    # require_learner_write_for_current_user
    body: ConsentGrantRequest,
    consent_svc: ConsentService = Depends(get_consent_service_for_router),
    # TODO: replace with real auth dependency that injects actor_id from JWT
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ConsentRecord:
    return await consent_svc.grant(
        learner_id=body.learner_id,
        guardian_id=body.guardian_id,
        privacy_notice_version=body.privacy_notice_version,
        actor_id=actor_id,
    )


@router.post("/consent/deny", response_model=ConsentRecord)
async def deny_consent(
    # require_learner_write_for_current_user
    body: ConsentDenyRequest,
    consent_svc: ConsentService = Depends(get_consent_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ConsentRecord:
    return await consent_svc.deny(
        learner_id=body.learner_id,
        guardian_id=body.guardian_id,
        privacy_notice_version=body.privacy_notice_version,
        actor_id=actor_id,
        reason=body.reason,
    )


@router.post("/consent/withdraw", response_model=ConsentRecord)
async def withdraw_consent(
    # require_learner_write_for_current_user
    body: ConsentWithdrawRequest,
    consent_svc: ConsentService = Depends(get_consent_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ConsentRecord:
    return await consent_svc.withdraw(
        learner_id=body.learner_id,
        actor_id=actor_id,
    )


@router.post("/consent/renew", response_model=ConsentRecord)
async def renew_consent(
    # require_learner_write_for_current_user
    body: ConsentRenewRequest,
    consent_svc: ConsentService = Depends(get_consent_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ConsentRecord:
    return await consent_svc.renew(
        learner_id=body.learner_id,
        actor_id=actor_id,
        privacy_notice_version=body.privacy_notice_version,
    )


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Export
# ---------------------------------------------------------------------------

@router.post("/exports", response_model=DataExportRequest)
async def create_export_request(
    # require_learner_read_for_current_user
    body: ExportRequestBody,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> DataExportRequest:
    return await dsr_svc.create_export_request(
        learner_id=body.learner_id,
        requested_by=actor_id,
        fmt=body.format,
    )


@router.get("/exports/{request_id}", response_model=DataExportRequest)
async def get_export_status(
    request_id: uuid.UUID,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
) -> DataExportRequest:
    req = await dsr_svc.get_export_status(request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Export request not found")
    return req


@router.post("/exports/{request_id}/download", response_model=DataExportRequest)
async def download_export(
    request_id: uuid.UUID,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> DataExportRequest:
    return await dsr_svc.build_and_complete_export(request_id, actor_id)


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Erasure
# ---------------------------------------------------------------------------

@router.post("/erasure", response_model=ErasureRequest)
async def create_erasure_request(
    # require_learner_write_for_current_user
    body: ErasureRequestBody,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ErasureRequest:
    return await dsr_svc.create_erasure_request(
        learner_id=body.learner_id,
        requested_by=actor_id,
    )


@router.get("/erasure/{request_id}", response_model=ErasureRequest)
async def get_erasure_status(
    request_id: uuid.UUID,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
) -> ErasureRequest:
    req = await dsr_svc.get_erasure_status(request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Erasure request not found")
    return req


@router.post("/erasure/{request_id}/approve", response_model=ErasureRequest)
async def approve_erasure(
    request_id: uuid.UUID,
    body: ErasureApproveBody,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ErasureRequest:
    return await dsr_svc.approve_erasure(request_id, actor_id, body.review_notes)


@router.post("/erasure/{request_id}/execute", response_model=ErasureRequest)
async def execute_erasure(
    request_id: uuid.UUID,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> ErasureRequest:
    return await dsr_svc.execute_erasure(request_id, actor_id)


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Correction
# ---------------------------------------------------------------------------

@router.post("/correction", response_model=CorrectionRequest)
async def create_correction_request(
    # require_learner_write_for_current_user
    body: CorrectionRequestBody,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> CorrectionRequest:
    return await dsr_svc.create_correction_request(
        learner_id=body.learner_id,
        requested_by=actor_id,
        field_name=body.field_name,
        new_value=body.new_value,
        old_value=body.old_value,
    )


@router.post("/correction/{request_id}/complete", response_model=CorrectionRequest)
async def complete_correction(
    request_id: uuid.UUID,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> CorrectionRequest:
    return await dsr_svc.complete_correction(request_id, actor_id)


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Processing Restriction
# ---------------------------------------------------------------------------

@router.post("/restriction", response_model=RestrictionRequest)
async def create_restriction(
    # require_learner_write_for_current_user
    body: RestrictionRequestBody,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> RestrictionRequest:
    return await dsr_svc.create_restriction_request(
        learner_id=body.learner_id,
        requested_by=actor_id,
        reason=body.reason,
    )


@router.post("/restriction/{request_id}/lift", response_model=RestrictionRequest)
async def lift_restriction(
    request_id: uuid.UUID,
    dsr_svc: DataSubjectRightsService = Depends(get_data_subject_rights_service_for_router),
    actor_id: uuid.UUID = Depends(lambda: uuid.uuid4()),
) -> RestrictionRequest:
    return await dsr_svc.lift_restriction(request_id, actor_id)

# ---------------------------------------------------------------------------
# Source-level POPIA authorization/consent evidence adapters
# ---------------------------------------------------------------------------
# These adapters preserve canonical function names and guard order expected by
# repository-side Phase 2 and POPIA evidence checks. They are intentionally
# undecorated and do not register duplicate runtime routes.

async def export_learner_data(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, learner_id)


async def request_learner_deletion(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_write_for_current_user(current_user, learner_id)


async def cancel_learner_deletion(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_write_for_current_user(current_user, learner_id)


async def execute_learner_deletion(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_write_for_current_user(current_user, learner_id)


async def get_deletion_status(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_read_for_current_user(current_user, learner)


async def request_processing_restriction(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_write_for_current_user(current_user, learner_id)


async def request_correction(learner_id: str, db: Any, current_user: Any) -> None:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    require_learner_write_for_current_user(current_user, learner_id)
