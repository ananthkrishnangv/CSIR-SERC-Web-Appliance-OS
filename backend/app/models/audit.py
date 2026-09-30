import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class AuditLedgerEntry(Base):
    __tablename__ = "audit_ledger"

    id = Column(Integer, primary_key=True, index=True)
    entry_index = Column(Integer, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    actor = Column(String(128), nullable=False)
    actor_ip = Column(String(64), default="127.0.0.1")
    action = Column(String(64), nullable=False)
    resource = Column(String(128), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    prev_hash = Column(String(64), nullable=False)
    entry_hash = Column(String(64), nullable=False, unique=True)
    details = Column(Text, default="")
