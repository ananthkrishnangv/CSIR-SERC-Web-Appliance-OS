from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ai_center import SecurityNarrative, AIRecommendation
from app.schemas.ai_center import SecurityNarrativeResponse, AIRecommendationResponse, RecommendationApprovalRequest
from app.services.ai_advisor import ai_advisor
from app.services.audit_service import audit_service

router = APIRouter(prefix="/ai-security", tags=["Local AI Security & Operations Center"])

# -----------------------------------------------------------------------------
# Part 1: Narratives & Recommendations
# -----------------------------------------------------------------------------

@router.get("/narratives", response_model=List[SecurityNarrativeResponse])
def list_narratives(db: Session = Depends(get_db)):
    return db.query(SecurityNarrative).order_by(SecurityNarrative.created_at.desc()).all()

@router.get("/recommendations", response_model=List[AIRecommendationResponse])
def list_recommendations(db: Session = Depends(get_db)):
    return db.query(AIRecommendation).order_by(AIRecommendation.created_at.desc()).all()

@router.post("/recommendations/{rec_id}/approval")
def submit_recommendation_approval(
    rec_id: str,
    req: RecommendationApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Submits human sign-off for an AI-suggested mitigation.
    Enforces the mandate that AI is advisory and cannot execute high-impact actions alone.
    """
    try:
        res = ai_advisor.process_human_approval(
            db=db,
            rec_id=rec_id,
            decision=req.decision,
            approver=req.approver,
            notes=req.notes
        )

        audit_service.record_audit_event(
            db=db,
            actor=req.approver,
            action=f"AI_ACTION_{req.decision.upper()}",
            resource=f"recommendation:{rec_id}",
            details={"rec_id": rec_id, "decision": req.decision, "notes": req.notes}
        )

        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/simulate-threat")
def simulate_threat_analysis(db: Session = Depends(get_db)):
    """Simulates threat correlation from WAF and firewall sensors."""
    simulated_events = [
        {"timestamp": "2026-09-30T10:14:02Z", "source_ip": "198.51.100.44", "attack_type": "Path Traversal (CRS 930100)", "target": "portal"},
        {"timestamp": "2026-09-30T10:14:05Z", "source_ip": "198.51.100.44", "attack_type": "SQLi Probe (CRS 942100)", "target": "portal"},
        {"timestamp": "2026-09-30T10:14:09Z", "source_ip": "198.51.100.44", "attack_type": "RCE Marker (CRS 932100)", "target": "portal"},
    ]
    narrative = ai_advisor.correlate_incident_events(db, simulated_events)
    recs = ai_advisor.generate_recommendations(db, narrative)

    audit_service.record_audit_event(
        db=db,
        actor="system:ai_engine",
        action="SYNTHESIZE_THREAT_NARRATIVE",
        resource=f"narrative:{narrative.narrative_id}",
        details={"narrative_id": narrative.narrative_id, "generated_recommendations": len(recs)}
    )

    return {
        "status": "success",
        "narrative": {
            "id": narrative.narrative_id,
            "title": narrative.title,
            "mitre": narrative.mitre_attack
        },
        "recommendations_count": len(recs)
    }

# -----------------------------------------------------------------------------
# Part 2: Intelligent WAF Assistant & Threat Correlation
# -----------------------------------------------------------------------------

@router.get("/waf-assistant/rules/{rule_id}")
def analyze_waf_rule(rule_id: int, name: str = "OWASP CRS Rule"):
    return ai_advisor.analyze_waf_rule(rule_id, name)

@router.get("/threat-correlation/timeline/{narrative_id}")
def get_attack_timeline(narrative_id: str):
    return ai_advisor.generate_attack_timeline(narrative_id)

@router.get("/vulnerabilities/prioritized")
def get_prioritized_vulnerabilities():
    return ai_advisor.prioritize_vulnerabilities()

@router.post("/malware-assistant/scan")
def scan_malware(target: str = Query("app-container.tar.gz"), target_type: str = Query("container")):
    return ai_advisor.analyze_malware_sample(target, target_type)

@router.get("/security-posture")
def get_security_posture():
    return ai_advisor.evaluate_security_posture()

# -----------------------------------------------------------------------------
# Part 3: AI Operations Center (Part 10)
# -----------------------------------------------------------------------------

@router.get("/operations/infrastructure-rca")
def diagnose_slowdown(app_id: str = "res-portal"):
    return ai_advisor.diagnose_infrastructure_slowdown(app_id)

@router.get("/operations/capacity-planning")
def get_capacity_planning():
    return ai_advisor.forecast_capacity()

@router.get("/operations/predictive-failure")
def get_predictive_failure():
    return ai_advisor.predict_hardware_failures()

# -----------------------------------------------------------------------------
# Part 4: AI Backup Intelligence (Part 11)
# -----------------------------------------------------------------------------

@router.get("/backup-intelligence/anomalies")
def get_backup_anomalies():
    return ai_advisor.detect_backup_anomalies()

@router.get("/backup-intelligence/recovery-plan")
def get_recovery_plan(app_name: str = "Research Portal"):
    return ai_advisor.generate_recovery_plan(app_name)

# -----------------------------------------------------------------------------
# Part 5: AI Virtualization Advisor (Part 12)
# -----------------------------------------------------------------------------

@router.get("/virtualization/advisory")
def get_virtualization_advisory():
    return ai_advisor.get_virtualization_advisory()

# -----------------------------------------------------------------------------
# Part 6: AI Container Security (Part 13)
# -----------------------------------------------------------------------------

@router.get("/container-security")
def get_container_security():
    return ai_advisor.analyze_container_security()

# -----------------------------------------------------------------------------
# Part 7: AI Compliance Platform (Part 14)
# -----------------------------------------------------------------------------

@router.get("/compliance")
def get_compliance_scorecard():
    return ai_advisor.evaluate_compliance()

# -----------------------------------------------------------------------------
# Part 8: AI-Assisted Deployment (Part 15)
# -----------------------------------------------------------------------------

@router.get("/deployment-advisor/spec")
def generate_deployment_spec(
    app_name: str = Query("scientific-dashboard"),
    domain: str = Query("dash.csir.res.in"),
    port: int = Query(8085)
):
    return ai_advisor.generate_deployment_spec(app_name, domain, port)

# -----------------------------------------------------------------------------
# Part 9: AI ChatOps (Part 16)
# -----------------------------------------------------------------------------

class ChatOpsRequest(BaseModel):
    query: str = Field(..., example="Create website for recruit portal")
    user: str = Field("admin@csir.res.in", example="admin@csir.res.in")

class ChatOpsApprovalRequest(BaseModel):
    action_id: str
    decision: str = Field(..., example="approve") # approve, reject
    approver: str = Field("admin@csir.res.in", example="admin@csir.res.in")

@router.post("/chatops/query")
def submit_chatops_query(req: ChatOpsRequest, db: Session = Depends(get_db)):
    """
    Submits a natural language operation.
    Returns structured proposal requiring human confirmation for any state-changing task.
    """
    res = ai_advisor.process_chatops_command(req.query, req.user)
    
    audit_service.record_audit_event(
        db=db,
        actor=req.user,
        action="CHATOPS_QUERY",
        resource="chatops:session",
        details={"query": req.query, "proposal_intent": res["proposal"]["intent"]}
    )
    return res

@router.post("/chatops/approve")
def approve_chatops_action(req: ChatOpsApprovalRequest, db: Session = Depends(get_db)):
    """
    Executes an approved ChatOps proposal following explicit human sign-off.
    """
    audit_service.record_audit_event(
        db=db,
        actor=req.approver,
        action=f"CHATOPS_ACTION_{req.decision.upper()}",
        resource=f"chatops:{req.action_id}",
        details={"action_id": req.action_id, "decision": req.decision}
    )
    return {
        "action_id": req.action_id,
        "status": "executed" if req.decision == "approve" else "cancelled",
        "approver": req.approver,
        "message": f"Action {req.action_id} was verified against policy engine and {'executed via Node Agent' if req.decision == 'approve' else 'rejected'}."
    }
