import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.api import (
    overview_router,
    applications_router,
    webhosting_router,
    proxy_router,
    ssl_router,
    security_router,
    ai_security_router,
    backups_router,
    updates_router,
    audit_router,
    system_router,
    auth_router
)
from app.models import (
    Application, WafRule, FirewallRule, SecurityIncident,
    BtrfsSnapshot, BackupRepository, BackupRun, DisasterRecoveryTest,
    SystemCertificate, ApplianceState
)
from app.services.audit_service import audit_service

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Control Plane API for CSIR Secure Web Appliance OS (openSUSE MicroOS based)"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Register API Routers
app.include_router(overview_router, prefix=settings.API_V1_STR)
app.include_router(applications_router, prefix=settings.API_V1_STR)
app.include_router(webhosting_router, prefix=settings.API_V1_STR)
app.include_router(proxy_router, prefix=settings.API_V1_STR)
app.include_router(ssl_router, prefix=settings.API_V1_STR)
app.include_router(security_router, prefix=settings.API_V1_STR)
app.include_router(ai_security_router, prefix=settings.API_V1_STR)
app.include_router(backups_router, prefix=settings.API_V1_STR)
app.include_router(updates_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)

STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_portal():
        return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "product": settings.PROJECT_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "immutable_root": True,
        "channel": settings.CURRENT_CHANNEL
    }

@app.on_event("startup")
def seed_baseline_data():
    """Seeds baseline data if database is fresh."""
    db = SessionLocal()
    try:
        # 1. Appliance State
        if not db.query(ApplianceState).first():
            state = ApplianceState(
                hostname="csir-swa-01",
                organisation="CSIR-SERC Chennai",
                channel="Stable",
                os_version="CSIR-SWA OS 1.0.0 (openSUSE MicroOS 2026.09)",
                active_snapshot=14,
                health_status="healthy",
                uptime_seconds=128400
            )
            db.add(state)
            db.commit()

        # 2. Baseline Applications (matching Section 8 mockup)
        if db.query(Application).count() == 0:
            apps = [
                Application(
                    app_id="res-portal",
                    name="Research Portal",
                    description="CSIR Public Research Projects & Publications Portal",
                    image="registry.csir.res.in/apps/research-portal:1.2.0",
                    digest="sha256:d8c5f948a123f8b375b42a00df87b9264871e98412431fae",
                    status="running",
                    health="healthy",
                    waf_mode="strict",
                    backup_status="current",
                    cpu_percent=22,
                    memory_mb=1024,
                    port=8080,
                    domain="research.csir.res.in",
                    is_rootless=True
                ),
                Application(
                    app_id="recruitment",
                    name="Recruitment",
                    description="National Scientific Recruitment and Event Portal",
                    image="registry.csir.res.in/apps/recruitment:2.4.1",
                    digest="sha256:4a8b79e13cf3526189db8a729e87bbef110298a0029b3841",
                    status="running",
                    health="healthy",
                    waf_mode="adaptive",
                    backup_status="current",
                    cpu_percent=38,
                    memory_mb=768,
                    port=8081,
                    domain="recruit.csir.res.in",
                    is_rootless=True
                ),
                Application(
                    app_id="lab-api",
                    name="Laboratory API",
                    description="SERC Scientific Sensor and High-Throughput Instrumentation API",
                    image="registry.csir.res.in/apps/lab-api:3.0.0",
                    digest="sha256:e901b2a95c81729b19df402319ef7612c6a084018274a123",
                    status="running",
                    health="warning",
                    waf_mode="strict",
                    backup_status="current",
                    cpu_percent=67,
                    memory_mb=1536,
                    port=8082,
                    domain="api.serc.res.in",
                    is_rootless=True
                )
            ]
            for a in apps:
                db.add(a)
            db.commit()

        # 3. WAF Rules (OWASP CRS v4 baseline)
        if db.query(WafRule).count() == 0:
            waf_rules = [
                WafRule(rule_id=920100, name="Invalid HTTP Request Line", category="Protocol", paranoia_level=1, action="deny", enabled=True),
                WafRule(rule_id=930100, name="Path Traversal Attack (LFI)", category="LFI", paranoia_level=1, action="deny", enabled=True),
                WafRule(rule_id=932100, name="Remote Command Execution (RCE)", category="RCE", paranoia_level=1, action="deny", enabled=True),
                WafRule(rule_id=941100, name="XSS Filter Evasion Attempt", category="XSS", paranoia_level=1, action="deny", enabled=True),
                WafRule(rule_id=942100, name="SQL Injection Attack Detection", category="SQLi", paranoia_level=1, action="deny", enabled=True),
            ]
            for r in waf_rules:
                db.add(r)
            db.commit()

        # 4. Firewall Rules
        if db.query(FirewallRule).count() == 0:
            fw_rules = [
                FirewallRule(chain="input", protocol="tcp", dport=80, source="0.0.0.0/0", action="accept", comment="HTTP redirect"),
                FirewallRule(chain="input", protocol="tcp", dport=443, source="0.0.0.0/0", action="accept", comment="HTTPS Reverse Proxy Ingress"),
                FirewallRule(chain="input", protocol="tcp", dport=8443, source="0.0.0.0/0", action="accept", comment="CSIR Appliance Management Portal"),
            ]
            for r in fw_rules:
                db.add(r)
            db.commit()

        # 5. Security Incidents (Matching Section 8: 1 Critical, 4 Medium)
        if db.query(SecurityIncident).count() == 0:
            incidents = [
                SecurityIncident(
                    incident_id="inc-2026-001",
                    title="Path Traversal & Remote Code Execution Probe against Research Portal",
                    severity="critical",
                    source_ip="198.51.100.44",
                    target_app="Research Portal",
                    attack_type="RCE / LFI Probe",
                    status="active",
                    mitre_technique="T1190",
                    details="Automated scanner initiated 47 high-velocity requests exploiting CVE-2026-4401 pattern."
                ),
                SecurityIncident(
                    incident_id="inc-2026-002",
                    title="SQL Injection attempt on recruitment portal candidate search",
                    severity="medium",
                    source_ip="203.0.113.89",
                    target_app="Recruitment",
                    attack_type="SQL Injection",
                    status="mitigated",
                    mitre_technique="T1190",
                    details="WAF Rule 942100 triggered. IP temporarily denied for 30 minutes."
                ),
                SecurityIncident(
                    incident_id="inc-2026-003",
                    title="Cross-Site Scripting (XSS) parameter injection",
                    severity="medium",
                    source_ip="192.0.2.112",
                    target_app="Research Portal",
                    attack_type="XSS",
                    status="mitigated",
                    mitre_technique="T1059",
                    details="Payload intercepted and sanitized by Coraza WAF."
                ),
                SecurityIncident(
                    incident_id="inc-2026-004",
                    title="Abnormal API burst on scientific data endpoint",
                    severity="medium",
                    source_ip="198.51.100.201",
                    target_app="Laboratory API",
                    attack_type="Rate Anomaly",
                    status="investigating",
                    mitre_technique="T1499",
                    details="Traffic rate exceeded 400 req/sec threshold."
                ),
                SecurityIncident(
                    incident_id="inc-2026-005",
                    title="TLS Protocol Downgrade attempt intercepted",
                    severity="medium",
                    source_ip="203.0.113.14",
                    target_app="Research Portal",
                    attack_type="Protocol Downgrade",
                    status="mitigated",
                    mitre_technique="T1557",
                    details="Attempted TLS 1.0 connection rejected by HAProxy edge."
                )
            ]
            for i in incidents:
                db.add(i)
            db.commit()

        # 6. Snapshots & Backups
        if db.query(BtrfsSnapshot).count() == 0:
            db.add(BtrfsSnapshot(
                snapshot_number=14,
                subvolume="/",
                description="CSIR-SWA OS 1.0.0 Base Verified Release",
                cleanup_type="important",
                is_pre_update=False
            ))
            db.commit()

        if db.query(BackupRepository).count() == 0:
            db.add(BackupRepository(
                repo_id="repo-worm-01",
                name="primary-worm-vault",
                backend_type="restic",
                uri="sftp://backup-vault.csir.res.in/srv/backup/csir-swa-01",
                encrypted=True,
                is_immutable=True,
                last_verified_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            ))
            db.commit()

        if db.query(DisasterRecoveryTest).count() == 0:
            db.add(DisasterRecoveryTest(
                test_id="dr-test-01",
                repository_name="primary-worm-vault",
                target_app="Research Portal",
                status="passed",
                measured_rto_seconds=38,
                measured_rpo_seconds=90,
                verified_hash="sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
                tested_at=datetime.datetime.utcnow() - datetime.timedelta(hours=14),
                details="Scheduled test restore verified complete integrity of database and static assets."
            ))
            db.commit()

        # 7. Initial Genesis Audit Event
        if db.query(audit_service.record_audit_event.__annotations__.get('return', None) or object).count() == 0:
            audit_service.record_audit_event(
                db=db,
                actor="system:installer",
                action="INITIALIZE_APPLIANCE",
                resource="appliance:csir-swa-01",
                details={
                    "event": "GENESIS_BOOT",
                    "immutable_baseline": "openSUSE MicroOS",
                    "certification": "CERT-In 2026.09 Baseline Compliant"
                }
            )

    finally:
        db.close()
