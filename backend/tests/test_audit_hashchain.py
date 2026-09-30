import pytest
from app.database import Base, engine, SessionLocal
from app.services.audit_service import audit_service
from app.models.audit import AuditLedgerEntry

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_hash_chain_creation_and_verification():
    db = SessionLocal()
    try:
        # Clear existing audit entries for pure test
        db.query(AuditLedgerEntry).delete()
        db.commit()

        # Add 3 entries in sequence
        e1 = audit_service.record_audit_event(db, "admin", "LOGIN", "system", {"ip": "10.0.0.1"})
        e2 = audit_service.record_audit_event(db, "admin", "DEPLOY_APP", "app:portal", {"version": "1.0"})
        e3 = audit_service.record_audit_event(db, "admin", "CREATE_SNAPSHOT", "snapshot:1", {"desc": "test"})

        assert e1.prev_hash == "0000000000000000000000000000000000000000000000000000000000000000"
        assert e2.prev_hash == e1.entry_hash
        assert e3.prev_hash == e2.entry_hash

        # Verify integrity
        report = audit_service.verify_audit_chain(db)
        assert report["is_valid"] is True
        assert report["total_entries"] == 3
        assert report["head_hash"] == e3.entry_hash

    finally:
        db.close()

def test_hash_chain_tamper_detection():
    db = SessionLocal()
    try:
        entry_to_tamper = db.query(AuditLedgerEntry).filter(AuditLedgerEntry.entry_index == 2).first()
        if entry_to_tamper:
            orig_actor = entry_to_tamper.actor
            entry_to_tamper.actor = "malicious_actor"
            db.commit()

            # Chain verification must FAIL
            report = audit_service.verify_audit_chain(db)
            assert report["is_valid"] is False
            assert "Tampering detected" in report["message"] or "broken at index" in report["message"]

            # Restore original actor to keep test state clean
            entry_to_tamper.actor = orig_actor
            db.commit()
    finally:
        db.close()
