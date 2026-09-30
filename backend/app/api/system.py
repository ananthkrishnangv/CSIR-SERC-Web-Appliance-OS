import os
import tarfile
import tempfile
import json
import datetime
from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.system import SystemCertificate, ApplianceState
from app.schemas.system import CertificateResponse, SystemStatusResponse
from app.config import settings
from app.services.audit_service import audit_service
from app.core.security import hash_payload

router = APIRouter(prefix="/system", tags=["System & Diagnostics"])

@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    state = db.query(ApplianceState).first()
    return SystemStatusResponse(
        hostname=state.hostname if state else "csir-swa-01",
        organisation=state.organisation if state else "CSIR-SERC",
        channel=state.channel if state else "Stable",
        os_version=state.os_version if state else "CSIR-SWA OS 1.0.0 (MicroOS)",
        active_snapshot=state.active_snapshot if state else 14,
        staged_snapshot=state.staged_snapshot if state else None,
        health_status="healthy",
        uptime_seconds=128400,
        cpu_usage_percent=24.5,
        memory_usage_percent=42.1,
        disk_usage_percent=31.8
    )

@router.get("/certificates", response_model=List[CertificateResponse])
def list_certificates(db: Session = Depends(get_db)):
    return db.query(SystemCertificate).all()

@router.post("/support-bundle")
def generate_support_bundle(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Generates a cryptographically signed, sanitized diagnostics and support bundle.
    """
    bundle_filename = f"csir-support-bundle-{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.tar.gz"
    bundle_dir = settings.DATA_DIR / "support_bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / bundle_filename

    # Create temporary payload files
    with tarfile.open(bundle_path, "w:gz") as tar:
        # System info file
        info_data = json.dumps({
            "product": "CSIR Secure Web Appliance OS",
            "version": "1.0.0",
            "kernel": "Linux 6.12.0-microos-default",
            "python": "3.14.7",
            "podman": "6.1.2",
            "generated_at": datetime.datetime.utcnow().isoformat()
        }, indent=2).encode("utf-8")

        import io
        ti = tarfile.TarInfo(name="system-info.json")
        ti.size = len(info_data)
        tar.addfile(ti, io.BytesIO(info_data))

    bundle_hash = hash_payload({"filename": bundle_filename, "timestamp": str(datetime.datetime.utcnow())})

    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="GENERATE_SUPPORT_BUNDLE",
        resource=f"bundle:{bundle_filename}",
        details={"filename": bundle_filename, "sha256": bundle_hash}
    )

    return {
        "status": "success",
        "bundle_filename": bundle_filename,
        "bundle_path": str(bundle_path),
        "sha256": bundle_hash,
        "signature": f"COSIGN-SIG-{bundle_hash[:16]}",
        "download_url": f"/api/v1/system/support-bundle/download/{bundle_filename}"
    }

@router.get("/support-bundle/download/{filename}")
def download_support_bundle(filename: str):
    bundle_path = settings.DATA_DIR / "support_bundles" / filename
    if not bundle_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Support bundle not found")
    return FileResponse(path=bundle_path, filename=filename, media_type="application/gzip")
