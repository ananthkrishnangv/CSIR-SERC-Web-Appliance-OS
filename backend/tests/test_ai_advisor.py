import pytest
from app.database import SessionLocal, Base, engine
from app.services.ai_advisor import ai_advisor
from app.core.policy_engine import policy_engine

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_ai_advisor_threat_synthesis():
    db = SessionLocal()
    try:
        events = [
            {"timestamp": "2026-09-30T12:00:00Z", "source_ip": "198.51.100.99", "attack_type": "SQLi Probe", "target": "portal"},
            {"timestamp": "2026-09-30T12:00:05Z", "source_ip": "198.51.100.99", "attack_type": "Path Traversal", "target": "portal"},
        ]
        narrative = ai_advisor.correlate_incident_events(db, events)
        assert narrative.narrative_id.startswith("nar-")
        assert "T1190" in narrative.mitre_attack
        assert narrative.confidence_score >= 0.9

        recs = ai_advisor.generate_recommendations(db, narrative)
        assert len(recs) == 2

        # Verify low-risk vs high-impact approval requirement
        rate_rec = next(r for r in recs if r.action_type == "rate_limit")
        assert rate_rec.approval_required == "none"

        stop_rec = next(r for r in recs if r.action_type == "stop_workload")
        assert stop_rec.approval_required == "human"

    finally:
        db.close()

def test_ai_guardrails_policy():
    # Verify policy engine blocks automated execution of high impact actions
    allowed, msg = policy_engine.evaluate_ai_action_policy("stop_workload", "high")
    assert allowed is False
    assert "Human Administrator approval" in msg

    allowed_crit, msg_crit = policy_engine.evaluate_ai_action_policy("delete_data", "critical")
    assert allowed_crit is False
    assert "Dual-Administrator" in msg_crit
