from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditLedgerEntry
from app.schemas.audit import AuditLedgerEntryResponse, AuditVerificationResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["Compliance & Audit Ledger"])

@router.get("/ledger", response_model=List[AuditLedgerEntryResponse])
def get_audit_ledger(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AuditLedgerEntry).order_by(AuditLedgerEntry.entry_index.desc()).limit(limit).all()

@router.get("/verify", response_model=AuditVerificationResponse)
def verify_ledger_cryptographic_integrity(db: Session = Depends(get_db)):
    """
    Verifies that every single entry in the hash chain satisfies:
    entry_hash == SHA256(prev_hash | index | timestamp | actor | action | resource | payload_hash)
    Detects any database tampering, alteration, or row deletion.
    """
    return audit_service.verify_audit_chain(db)

@router.get("/cert-in-export")
def export_cert_in_compliance_dossier(db: Session = Depends(get_db)):
    """
    Exports a certified incident and administrative audit package
    formatted for CERT-In regulatory compliance and 180-day retention verification.
    """
    return audit_service.export_cert_in_report(db)
