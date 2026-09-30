import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base

class BtrfsSnapshot(Base):
    __tablename__ = "btrfs_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_number = Column(Integer, unique=True, index=True, nullable=False)
    subvolume = Column(String(128), default="/")
    description = Column(String(256), nullable=False)
    cleanup_type = Column(String(32), default="timeline") # timeline, number, important
    is_pre_update = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BackupRun(Base):
    __tablename__ = "backup_runs"

    id = Column(Integer, primary_key=True, index=True)
    backup_id = Column(String(64), unique=True, index=True, nullable=False)
    target_type = Column(String(32), default="restic")    # restic, btrfs_send, postgresql_pitr
    repository_name = Column(String(128), nullable=False)
    status = Column(String(32), default="completed")       # completed, in_progress, failed
    files_new = Column(Integer, default=0)
    bytes_transferred = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=12)
    snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BackupRepository(Base):
    __tablename__ = "backup_repositories"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    backend_type = Column(String(32), default="restic")    # restic, s3_immutable, sftp_worm
    uri = Column(String(256), nullable=False)
    encrypted = Column(Boolean, default=True)
    is_immutable = Column(Boolean, default=True)
    last_verified_at = Column(DateTime, nullable=True)

class DisasterRecoveryTest(Base):
    __tablename__ = "dr_tests"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(64), unique=True, index=True, nullable=False)
    repository_name = Column(String(128), nullable=False)
    target_app = Column(String(128), nullable=False)
    status = Column(String(32), default="passed")          # passed, failed
    measured_rto_seconds = Column(Integer, default=45)     # Recovery Time Objective
    measured_rpo_seconds = Column(Integer, default=120)    # Recovery Point Objective
    verified_hash = Column(String(128), nullable=False)
    tested_at = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text, default="")
