from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.system import ApplianceState
from app.schemas.system import TransactionalUpdateTriggerRequest
from app.services.update_service import update_service
from app.services.audit_service import audit_service
from app.config import settings

router = APIRouter(prefix="/updates", tags=["Transactional Updates & Lifecycle"])

@router.get("/status")
def get_update_status(db: Session = Depends(get_db)):
    state = db.query(ApplianceState).first()
    return {
        "channel": state.channel if state else settings.CURRENT_CHANNEL,
        "available_channels": settings.SUPPORTED_CHANNELS,
        "active_snapshot": state.active_snapshot if state else 14,
        "staged_snapshot": state.staged_snapshot if state else None,
        "reboot_required": state.staged_snapshot is not None if state else False,
        "base_os": "openSUSE MicroOS (Transactional-Update Engine)"
    }

@router.post("/stage")
def stage_transactional_update(req: TransactionalUpdateTriggerRequest, db: Session = Depends(get_db)):
    res = update_service.stage_update(db, target_channel=req.target_channel)

    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="STAGE_TRANSACTIONAL_UPDATE",
        resource="system:os_root",
        details=res
    )
    return res

@router.post("/rollback")
def trigger_rollback(db: Session = Depends(get_db)):
    res = update_service.trigger_rollback(db)

    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="TRIGGER_OS_ROLLBACK",
        resource="system:os_root",
        details=res
    )
    return res
