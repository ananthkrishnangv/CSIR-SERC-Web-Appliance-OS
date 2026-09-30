import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BtrfsSnapshotCreate(BaseModel):
    description: str = Field(..., example="Pre-deployment snapshot for Portal v2")
    cleanup_type: str = Field("timeline", example="timeline")

class BtrfsSnapshotResponse(BaseModel):
    id: int
    snapshot_number: int
    subvolume: str
    description: str
    cleanup_type: str
    is_pre_update: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class BackupRunResponse(BaseModel):
    id: int
    backup_id: str
    target_type: str
    repository_name: str
    status: str
    files_new: int
    bytes_transferred: int
    duration_seconds: int
    snapshot_id: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class DisasterRecoveryTestResponse(BaseModel):
    id: int
    test_id: str
    repository_name: str
    target_app: str
    status: str
    measured_rto_seconds: int
    measured_rpo_seconds: int
    verified_hash: str
    tested_at: datetime.datetime
    details: str

    class Config:
        from_attributes = True
