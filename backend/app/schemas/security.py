import datetime
from pydantic import BaseModel, Field

class WafRuleResponse(BaseModel):
    id: int
    rule_id: int
    name: str
    category: str
    paranoia_level: int
    action: str
    enabled: bool

    class Config:
        from_attributes = True

class WafToggleRequest(BaseModel):
    enabled: bool

class FirewallRuleCreate(BaseModel):
    chain: str = "input"
    protocol: str = "tcp"
    dport: int
    source: str = "0.0.0.0/0"
    action: str = "accept"
    comment: str = ""

class FirewallRuleResponse(FirewallRuleCreate):
    id: int
    enabled: bool

    class Config:
        from_attributes = True

class SecurityIncidentResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    severity: str
    source_ip: str
    target_app: str
    attack_type: str
    status: str
    mitre_technique: str
    detected_at: datetime.datetime
    details: str

    class Config:
        from_attributes = True
