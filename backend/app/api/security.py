from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.security import WafRule, FirewallRule, SecurityIncident
from app.schemas.security import (
    WafRuleResponse, WafToggleRequest,
    FirewallRuleCreate, FirewallRuleResponse,
    SecurityIncidentResponse
)
from app.services.security_service import security_engine
from app.services.node_agent import node_agent_client
from app.services.audit_service import audit_service

router = APIRouter(prefix="/security", tags=["Security & Protection"])

@router.get("/waf/rules", response_model=List[WafRuleResponse])
def list_waf_rules(db: Session = Depends(get_db)):
    return db.query(WafRule).order_by(WafRule.rule_id.asc()).all()

@router.post("/waf/rules/{rule_id}/toggle")
def toggle_waf_rule(rule_id: int, req: WafToggleRequest, db: Session = Depends(get_db)):
    rule = db.query(WafRule).filter(WafRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="WAF rule not found")

    rule.enabled = req.enabled
    db.commit()

    audit_service.record_audit_event(
        db=db,
        actor="security_officer@csir.res.in",
        action="TOGGLE_WAF_RULE",
        resource=f"waf_rule:{rule_id}",
        details={"rule_id": rule_id, "name": rule.name, "enabled": req.enabled}
    )
    return {"status": "success", "rule_id": rule_id, "enabled": rule.enabled}

@router.get("/firewall/rules", response_model=List[FirewallRuleResponse])
def list_firewall_rules(db: Session = Depends(get_db)):
    return db.query(FirewallRule).all()

@router.post("/firewall/rules", response_model=FirewallRuleResponse)
def create_firewall_rule(req: FirewallRuleCreate, db: Session = Depends(get_db)):
    new_rule = FirewallRule(
        chain=req.chain,
        protocol=req.protocol,
        dport=req.dport,
        source=req.source,
        action=req.action,
        comment=req.comment,
        enabled=True
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    # Recompile and apply nftables ruleset via Node Agent
    all_rules = db.query(FirewallRule).filter(FirewallRule.enabled == True).all()
    open_ports = [r.dport for r in all_rules]
    security_engine.generate_nftables_rules(open_ports)
    node_agent_client.execute_action("NFTABLES_APPLY_RULESET", {"ruleset": "csir-firewall.nft"})

    audit_service.record_audit_event(
        db=db,
        actor="security_officer@csir.res.in",
        action="ADD_FIREWALL_RULE",
        resource=f"firewall_rule:{new_rule.id}",
        details={"dport": req.dport, "protocol": req.protocol, "action": req.action}
    )

    return new_rule

@router.get("/incidents", response_model=List[SecurityIncidentResponse])
def list_security_incidents(db: Session = Depends(get_db)):
    return db.query(SecurityIncident).order_by(SecurityIncident.detected_at.desc()).all()
