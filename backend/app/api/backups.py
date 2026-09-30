from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.backup import BtrfsSnapshot, BackupRun, DisasterRecoveryTest
from app.schemas.backup import (
    BtrfsSnapshotCreate, BtrfsSnapshotResponse,
    BackupRunResponse, DisasterRecoveryTestResponse
)
from app.services.backup_service import backup_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/backups", tags=["Data Protection & Backups"])

@router.get("/snapshots", response_model=List[BtrfsSnapshotResponse])
def list_snapshots(db: Session = Depends(get_db)):
    return db.query(BtrfsSnapshot).order_by(BtrfsSnapshot.created_at.desc()).all()

@router.post("/snapshots", response_model=BtrfsSnapshotResponse)
def create_snapshot(req: BtrfsSnapshotCreate, db: Session = Depends(get_db)):
    snap = backup_service.create_snapshot(
        db=db,
        description=req.description,
        cleanup_type=req.cleanup_type,
        is_pre_update=False
    )

    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="CREATE_BTRFS_SNAPSHOT",
        resource=f"snapshot:{snap.snapshot_number}",
        details={"snapshot_id": snap.snapshot_number, "desc": req.description}
    )
    return snap

@router.get("/runs", response_model=List[BackupRunResponse])
def list_backup_runs(db: Session = Depends(get_db)):
    return db.query(BackupRun).order_by(BackupRun.created_at.desc()).all()

@router.post("/runs/trigger", response_model=BackupRunResponse)
def trigger_backup_run(db: Session = Depends(get_db)):
    run = backup_service.run_restic_backup(db)

    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="RUN_RESTIC_BACKUP",
        resource=f"backup:{run.backup_id}",
        details={"backup_id": run.backup_id, "bytes": run.bytes_transferred}
    )
    return run

@router.get("/dr-tests", response_model=List[DisasterRecoveryTestResponse])
def list_dr_tests(db: Session = Depends(get_db)):
    return db.query(DisasterRecoveryTest).order_by(DisasterRecoveryTest.tested_at.desc()).all()

@router.post("/dr-tests/trigger", response_model=DisasterRecoveryTestResponse)
def trigger_dr_drill(db: Session = Depends(get_db)):
    test = backup_service.run_dr_restore_drill(db)

    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="EXECUTE_DR_DRILL",
        resource=f"dr_test:{test.test_id}",
        details={"test_id": test.test_id, "status": test.status, "measured_rto": test.measured_rto_seconds}
    )
    return test
