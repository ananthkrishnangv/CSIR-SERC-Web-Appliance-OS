import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    image = Column(String(256), nullable=False)
    digest = Column(String(128), nullable=False)
    status = Column(String(32), default="running")  # running, stopped, degraded, error
    health = Column(String(32), default="healthy")  # healthy, warning, critical
    waf_mode = Column(String(32), default="strict") # strict, adaptive, learning, disabled
    backup_status = Column(String(32), default="current") # current, pending, failed
    cpu_percent = Column(Integer, default=15)
    memory_mb = Column(Integer, default=256)
    port = Column(Integer, nullable=False)
    domain = Column(String(128), nullable=False)
    is_rootless = Column(Boolean, default=True)
    quadlet_path = Column(String(256), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
