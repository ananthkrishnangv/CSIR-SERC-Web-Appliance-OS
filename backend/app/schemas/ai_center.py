import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SecurityNarrativeResponse(BaseModel):
    id: int
    narrative_id: str
    title: str
    summary: str
    evidence: str
    confidence_score: float
    mitre_attack: str
    model_version: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class AIRecommendationResponse(BaseModel):
    id: int
    rec_id: str
    narrative_id: Optional[str] = None
    title: str
    action_type: str
    impact_level: str
    approval_required: str
    status: str
    evidence_citation: str
    approved_by: Optional[str] = None
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class RecommendationApprovalRequest(BaseModel):
    decision: str = Field(..., example="approve") # approve, reject
    notes: Optional[str] = None
    approver: str = Field("admin@csir.res.in", example="admin@csir.res.in")
