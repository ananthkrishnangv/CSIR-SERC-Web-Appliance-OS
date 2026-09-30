from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ai_center import SecurityNarrative, AIRecommendation
from app.schemas.ai_center import SecurityNarrativeResponse, AIRecommendationResponse, RecommendationApprovalRequest
from app.services.ai_advisor import ai_advisor
from app.services.audit_service import audit_service

router = APIRouter(prefix="/ai-security", tags=["Local AI Security Center"])

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
    """
    Simulates correlation of incoming WAF/Suricata attack events into an AI incident narrative.
    """
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
