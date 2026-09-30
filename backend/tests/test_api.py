import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["immutable_root"] is True

def test_overview_endpoint(client):
    res = client.get("/api/v1/overview")
    assert res.status_code == 200
    data = res.json()
    assert "headline_metrics" in data
    assert data["headline_metrics"]["health_score"] == "98%"
    assert "applications" in data
    assert len(data["applications"]) >= 3

def test_deploy_application_flow(client):
    rand_suffix = uuid.uuid4().hex[:6]
    new_app = {
        "name": f"SERC Sensor Dashboard {rand_suffix}",
        "description": "Real-time strain gauge telemetry",
        "image": "registry.csir.res.in/apps/serc-sensor:1.0.0",
        "port": 8089,
        "domain": f"sensor-{rand_suffix}.serc.res.in",
        "waf_mode": "strict",
        "cpu_limit": 30,
        "memory_mb": 512
    }
    res = client.post("/api/v1/applications", json=new_app)
    assert res.status_code in [200, 201]
    data = res.json()
    assert data["name"] == f"SERC Sensor Dashboard {rand_suffix}"
    assert data["is_rootless"] is True
    assert data["quadlet_path"] != ""

def test_waf_rules_listing_and_toggle(client):
    res = client.get("/api/v1/security/waf/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 5

    # Toggle first rule
    rule_id = rules[0]["rule_id"]
    res_toggle = client.post(f"/api/v1/security/waf/rules/{rule_id}/toggle", json={"enabled": False})
    assert res_toggle.status_code == 200
    assert res_toggle.json()["enabled"] is False

def test_audit_verification_endpoint(client):
    res = client.get("/api/v1/audit/verify")
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["total_entries"] > 0
