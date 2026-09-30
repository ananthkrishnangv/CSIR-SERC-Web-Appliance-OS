import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base

class SystemCertificate(Base):
    __tablename__ = "system_certificates"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(128), unique=True, index=True, nullable=False)
    issuer = Column(String(128), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True)
    fingerprint = Column(String(128), nullable=False)

class ApplianceState(Base):
    __tablename__ = "appliance_state"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(128), default="csir-swa-01")
    organisation = Column(String(128), default="CSIR-SERC")
    channel = Column(String(32), default="Stable")
    os_version = Column(String(64), default="CSIR-SWA OS 1.0.0 (MicroOS)")
    active_snapshot = Column(Integer, default=14)
    staged_snapshot = Column(Integer, nullable=True)
    health_status = Column(String(32), default="healthy")
    uptime_seconds = Column(Integer, default=124500)
    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow)
