import datetime
from pydantic import BaseModel

class AuditLedgerEntryResponse(BaseModel):
    id: int
    entry_index: int
    timestamp: datetime.datetime
    actor: str
    actor_ip: str
    action: str
    resource: str
    payload_hash: str
    prev_hash: str
    entry_hash: str
    details: str

    class Config:
        from_attributes = True

class AuditVerificationResponse(BaseModel):
    total_entries: int
    is_valid: bool
    verified_at: datetime.datetime
    head_hash: str
    message: str
