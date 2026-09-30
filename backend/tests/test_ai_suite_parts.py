import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_waf_assistant_analyzer():
    res = client.get("/api/v1/ai-security/waf-assistant/rules/942100?name=SQLi")
    assert res.status_code == 200
    data = res.json()
    assert data["rule_id"] == 942100
    assert "SQL injection" in data["explanation"]
    assert data["risk_score"] == 8.5

def test_attack_timeline():
    res = client.get("/api/v1/ai-security/threat-correlation/timeline/nar-test")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 3
    assert any("Coraza WAF" in e["source"] for e in events)

def test_vulnerability_prioritization():
    res = client.get("/api/v1/ai-security/vulnerabilities/prioritized")
    assert res.status_code == 200
    vulns = res.json()
    assert len(vulns) >= 3
    assert vulns[0]["priority"] == "Critical"
    assert "CVE" in vulns[0]["cve_id"]

def test_malware_analysis_assistant():
    res = client.post("/api/v1/ai-security/malware-assistant/scan?target=suspicious-binary.elf&target_type=container")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "suspicious_markers_detected"
    assert len(data["malware_indicators"]) > 0

def test_security_posture_advisor():
    res = client.get("/api/v1/ai-security/security-posture")
    assert res.status_code == 200
    data = res.json()
    assert data["overall_security_score"] > 90
    assert len(data["categories"]) >= 5

def test_infrastructure_rca_diagnostics():
    res = client.get("/api/v1/ai-security/operations/infrastructure-rca?app_id=res-portal")
    assert res.status_code == 200
    data = res.json()
    assert "root_cause_analysis" in data
    assert "PostgreSQL" in data["root_cause_analysis"]["primary_bottleneck"]
    assert len(data["recommendations"]) >= 1

def test_capacity_planning_forecast():
    res = client.get("/api/v1/ai-security/operations/capacity-planning")
    assert res.status_code == 200
    data = res.json()
    assert "storage_forecast" in data
    assert data["storage_forecast"]["projected_1_year_gb"] > 500

def test_predictive_failure_analysis():
    res = client.get("/api/v1/ai-security/operations/predictive-failure")
    assert res.status_code == 200
    data = res.json()
    assert data["health_score"] > 95
    assert len(data["devices"]) >= 2

def test_backup_anomaly_detection_and_recovery():
    res = client.get("/api/v1/ai-security/backup-intelligence/anomalies")
    assert res.status_code == 200
    data = res.json()
    assert data["ransomware_indicators"] == "None detected"

    rec_res = client.get("/api/v1/ai-security/backup-intelligence/recovery-plan?app_name=Research%20Portal")
    assert rec_res.status_code == 200
    plan = rec_res.json()
    assert len(plan["dependency_map"]) >= 4

def test_virtualization_advisory():
    res = client.get("/api/v1/ai-security/virtualization/advisory")
    assert res.status_code == 200
    data = res.json()
    assert "KVM" in data["hypervisor"]
    assert len(data["vm_health_advisor"]["vms"]) >= 3

def test_container_security():
    res = client.get("/api/v1/ai-security/container-security")
    assert res.status_code == 200
    data = res.json()
    assert "rootless" in data["rootless_enforcement"].lower()

def test_compliance_evaluation():
    res = client.get("/api/v1/ai-security/compliance")
    assert res.status_code == 200
    data = res.json()
    assert data["compliance_summary"]["overall_score"] > 90
    standards = [s["name"] for s in data["standards"]]
    assert any("CERT-In" in s for s in standards)
    assert any("GIGW" in s for s in standards)
    assert any("ISO" in s for s in standards)

def test_deployment_advisor():
    res = client.get("/api/v1/ai-security/deployment-advisor/spec?app_name=lab-portal&domain=lab.csir.res.in&port=8088")
    assert res.status_code == 200
    spec = res.json()
    assert "generated_quadlet" in spec
    assert "generated_waf_policy" in spec
    assert "generated_reverse_proxy" in spec

def test_chatops_governance_workflow():
    # 1. State-changing query requiring human approval
    res = client.post("/api/v1/ai-security/chatops/query", json={
        "query": "Create website for new laboratory portal",
        "user": "admin@csir.res.in"
    })
    assert res.status_code == 200
    proposal = res.json()["proposal"]
    assert proposal["approval_required"] is True
    assert proposal["governance_status"] == "AWAITING_HUMAN_APPROVAL"
    action_id = proposal["action_id"]

    # 2. Human approval sign-off
    appr_res = client.post("/api/v1/ai-security/chatops/approve", json={
        "action_id": action_id,
        "decision": "approve",
        "approver": "secops@csir.res.in"
    })
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "executed"
