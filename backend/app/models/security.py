import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base

class WafRule(Base):
    __tablename__ = "waf_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)  # SQLi, XSS, RCE, LFI, Protocol
    paranoia_level = Column(Integer, default=1)
    action = Column(String(32), default="deny")     # deny, drop, log
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class FirewallRule(Base):
    __tablename__ = "firewall_rules"

    id = Column(Integer, primary_key=True, index=True)
    chain = Column(String(32), nullable=False)      # input, forward, output
    protocol = Column(String(16), default="tcp")
    dport = Column(Integer, nullable=False)
    source = Column(String(64), default="0.0.0.0/0")
    action = Column(String(16), default="accept")   # accept, drop, reject
    comment = Column(String(128), default="")
    enabled = Column(Boolean, default=True)

class SecurityIncident(Base):
    __tablename__ = "security_incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), default="medium") # critical, high, medium, low
    source_ip = Column(String(64), nullable=False)
    target_app = Column(String(128), default="")
    attack_type = Column(String(64), nullable=False)
    status = Column(String(32), default="active")   # active, mitigated, investigating, resolved
    mitre_technique = Column(String(64), default="")
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text, default="")
