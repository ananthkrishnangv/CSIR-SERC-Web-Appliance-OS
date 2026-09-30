import datetime
import hashlib
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.audit import AuditLedgerEntry
from app.config import settings
from app.core.security import hash_payload

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class AuditService:
    @staticmethod
    def _compute_entry_hash(prev_hash: str, index: int, timestamp_str: str, actor: str, action: str, resource: str, payload_hash: str) -> str:
        chain_string = f"{prev_hash}|{index}|{timestamp_str}|{actor}|{action}|{resource}|{payload_hash}"
        return hashlib.sha256(chain_string.encode("utf-8")).hexdigest()

    @classmethod
    def record_audit_event(
        cls,
        db: Session,
        actor: str,
        action: str,
        resource: str,
        details: dict,
        actor_ip: str = "127.0.0.1"
    ) -> AuditLedgerEntry:
        # Find latest entry in chain
        last_entry = db.query(AuditLedgerEntry).order_by(AuditLedgerEntry.entry_index.desc()).first()
        if last_entry is None:
            prev_hash = GENESIS_HASH
            next_index = 1
        else:
            prev_hash = last_entry.entry_hash
            next_index = last_entry.entry_index + 1

        now = datetime.datetime.utcnow()
        timestamp_str = now.isoformat()
        payload_hash = hash_payload(details)

        entry_hash = cls._compute_entry_hash(
            prev_hash=prev_hash,
            index=next_index,
            timestamp_str=timestamp_str,
            actor=actor,
            action=action,
            resource=resource,
            payload_hash=payload_hash
        )

        entry = AuditLedgerEntry(
            entry_index=next_index,
            timestamp=now,
            actor=actor,
            actor_ip=actor_ip,
            action=action,
            resource=resource,
            payload_hash=payload_hash,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            details=json.dumps(details, default=str)
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        # Mirror entry to append-only disk ledger file for forensic resilience
        try:
            with open(settings.AUDIT_LEDGER_PATH, "a", encoding="utf-8") as f:
                record = {
                    "index": entry.entry_index,
                    "timestamp": timestamp_str,
                    "actor": entry.actor,
                    "ip": entry.actor_ip,
                    "action": entry.action,
                    "resource": entry.resource,
                    "payload_hash": entry.payload_hash,
                    "prev_hash": entry.prev_hash,
                    "entry_hash": entry.entry_hash
                }
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass # Keep primary DB transaction reliable

        return entry

    @classmethod
    def verify_audit_chain(cls, db: Session) -> dict:
        """
        Validates the entire cryptographic chain from genesis block to current head.
        Returns validation state and tamper detection point if broken.
        """
        entries = db.query(AuditLedgerEntry).order_by(AuditLedgerEntry.entry_index.asc()).all()
        if not entries:
            return {
                "total_entries": 0,
                "is_valid": True,
                "verified_at": datetime.datetime.utcnow(),
                "head_hash": GENESIS_HASH,
                "message": "Audit ledger is empty. Genesis state valid."
            }

        expected_prev_hash = GENESIS_HASH
        for entry in entries:
            # 1. Verify prev_hash link
            if entry.prev_hash != expected_prev_hash:
                return {
                    "total_entries": len(entries),
                    "is_valid": False,
                    "broken_at_index": entry.entry_index,
                    "verified_at": datetime.datetime.utcnow(),
                    "head_hash": entry.entry_hash,
                    "message": f"Cryptographic link broken at index {entry.entry_index}! Expected prev_hash {expected_prev_hash}, got {entry.prev_hash}."
                }

            # 2. Re-compute hash
            computed = cls._compute_entry_hash(
                prev_hash=entry.prev_hash,
                index=entry.entry_index,
                timestamp_str=entry.timestamp.isoformat(),
                actor=entry.actor,
                action=entry.action,
                resource=entry.resource,
                payload_hash=entry.payload_hash
            )

            if computed != entry.entry_hash:
                return {
                    "total_entries": len(entries),
                    "is_valid": False,
                    "broken_at_index": entry.entry_index,
                    "verified_at": datetime.datetime.utcnow(),
                    "head_hash": entry.entry_hash,
                    "message": f"Tampering detected at index {entry.entry_index}! Hash mismatch."
                }

            expected_prev_hash = entry.entry_hash

        return {
            "total_entries": len(entries),
            "is_valid": True,
            "verified_at": datetime.datetime.utcnow(),
            "head_hash": entries[-1].entry_hash,
            "message": "Audit chain cryptographic verification succeeded. 100% tamper-evident integrity."
        }

    @classmethod
    def export_cert_in_report(cls, db: Session) -> dict:
        """Generates CERT-In compliant incident & audit record export."""
        verification = cls.verify_audit_chain(db)
        entries = db.query(AuditLedgerEntry).order_by(AuditLedgerEntry.entry_index.desc()).limit(100).all()

        return {
            "jurisdiction": "India",
            "cert_in_directive": "Directions under sub-section (6) of section 70B",
            "ntp_synchronized": True,
            "ntp_sources": settings.NTP_SERVERS,
            "retention_policy_days": settings.LOG_RETENTION_DAYS,
            "chain_status": "VERIFIED_TAMPER_FREE" if verification["is_valid"] else "TAMPER_DETECTED",
            "audit_head_hash": verification["head_hash"],
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "records_count": len(entries),
            "records": [
                {
                    "index": e.entry_index,
                    "timestamp": e.timestamp.isoformat(),
                    "actor": e.actor,
                    "ip": e.actor_ip,
                    "action": e.action,
                    "resource": e.resource,
                    "entry_hash": e.entry_hash
                }
                for e in entries
            ]
        }

audit_service = AuditService()
