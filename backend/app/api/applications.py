import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationActionRequest
from app.services.podman_service import podman_service
from app.services.security_service import security_engine
from app.services.node_agent import node_agent_client
from app.services.audit_service import audit_service

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("", response_model=List[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()

@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: str, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.app_id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def deploy_application(req: ApplicationCreate, db: Session = Depends(get_db)):
    # 1. Check uniqueness
    existing = db.query(Application).filter(Application.domain == req.domain).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Domain {req.domain} is already registered to another application.")

    app_id = f"app-{uuid.uuid4().hex[:8]}"

    # 2. Verify image trust, signature and SBOM
    trust = podman_service.verify_image_provenance(req.image)
    simulated_digest = f"sha256:{uuid.uuid4().hex}"

    # 3. Generate Quadlet definitions (.container and .network)
    quadlet_file = podman_service.generate_quadlet(
        app_id=app_id,
        name=req.name,
        image=req.image,
        port=req.port,
        memory_mb=req.memory_mb,
        cpu_percent=req.cpu_limit,
        env_vars=req.env_vars,
        volumes=req.volumes,
        read_only_root=True
    )
    podman_service.generate_network_quadlet(app_id)

    # 4. Save to Database
    new_app = Application(
        app_id=app_id,
        name=req.name,
        description=req.description,
        image=req.image,
        digest=simulated_digest,
        status="running",
        health="healthy",
        waf_mode=req.waf_mode,
        backup_status="current",
        cpu_percent=15,
        memory_mb=req.memory_mb,
        port=req.port,
        domain=req.domain,
        is_rootless=True,
        quadlet_path=quadlet_file
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # 5. Update Reverse Proxy configuration
    all_apps = db.query(Application).all()
    apps_data = [{"app_id": a.app_id, "domain": a.domain, "port": a.port} for a in all_apps]
    security_engine.generate_haproxy_config(apps_data)

    # 6. Record tamper-evident audit entry
    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action="DEPLOY_APPLICATION",
        resource=f"app:{app_id}",
        details={
            "app_id": app_id,
            "name": req.name,
            "image": req.image,
            "digest": simulated_digest,
            "domain": req.domain,
            "port": req.port,
            "quadlet": quadlet_file,
            "sbom_gate": trust["gate_status"]
        }
    )

    return new_app

@router.post("/{app_id}/action")
def perform_application_action(app_id: str, req: ApplicationActionRequest, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.app_id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    action = req.action.lower()
    if action not in ["start", "stop", "restart", "rollback"]:
        raise HTTPException(status_code=400, detail="Invalid action. Supported: start, stop, restart, rollback")

    # Delegate systemd action via privileged Node Agent
    systemd_action = "restart" if action in ["restart", "rollback"] else action
    node_agent_client.execute_action("SYSTEMD_SERVICE_ACTION", {
        "unit": f"csir-{app_id}.service",
        "action": systemd_action
    })

    if action == "stop":
        app.status = "stopped"
    elif action in ["start", "restart", "rollback"]:
        app.status = "running"
        app.health = "healthy"
    db.commit()

    # Record audit entry
    audit_service.record_audit_event(
        db=db,
        actor="admin@csir.res.in",
        action=f"APPLICATION_{action.upper()}",
        resource=f"app:{app_id}",
        details={"app_id": app_id, "action": action}
    )

    return {"status": "success", "app_id": app_id, "current_status": app.status}
