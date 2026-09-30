import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from app.database import Base

class SecurityNarrative(Base):
    __tablename__ = "security_narratives"

    id = Column(Integer, primary_key=True, index=True)
    narrative_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(256), nullable=False)
    summary = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)          # Cited evidence logs & events
    confidence_score = Column(Float, default=0.85)   # 0.0 to 1.0
    mitre_attack = Column(String(128), default="")   # e.g., T1190, T1059
    model_version = Column(String(64), default="CSIR-SecModel-Local-v1.2")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    rec_id = Column(String(64), unique=True, index=True, nullable=False)
    narrative_id = Column(String(64), index=True, nullable=True)
    title = Column(String(256), nullable=False)
    action_type = Column(String(64), nullable=False)  # rate_limit, isolate_workload, patch_container, rotate_keys
    impact_level = Column(String(32), default="medium") # low, medium, high, critical
    approval_required = Column(String(32), default="human") # none, human, dual_admin
    status = Column(String(32), default="pending")    # pending, approved, rejected, executed, expired
    evidence_citation = Column(Text, default="")
    command_payload = Column(Text, default="")        # JSON payload sent to Node Agent
    approved_by = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(64), nullable=False)       # waf, proxy, suricata, podman
    score = Column(Float, default=0.5)
    description = Column(String(256), nullable=False)
    raw_event = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
