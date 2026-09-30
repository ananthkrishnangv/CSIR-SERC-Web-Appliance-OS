import datetime
from typing import Optional
from pydantic import BaseModel

class CertificateResponse(BaseModel):
    id: int
    domain: str
    issuer: str
    valid_from: datetime.datetime
    valid_to: datetime.datetime
    auto_renew: bool
    fingerprint: str

    class Config:
        from_attributes = True

class SystemStatusResponse(BaseModel):
    hostname: str
    organisation: str
    channel: str
    os_version: str
    active_snapshot: int
    staged_snapshot: Optional[int]
    health_status: str
    uptime_seconds: int
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float

class TransactionalUpdateTriggerRequest(BaseModel):
    target_channel: Optional[str] = None
    force: bool = False
