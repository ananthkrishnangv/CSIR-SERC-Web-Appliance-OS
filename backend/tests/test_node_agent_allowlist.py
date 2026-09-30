import pytest
from app.services.node_agent import node_agent_client
from node_agent.agent import PrivilegedNodeAgent
from app.core.policy_engine import policy_engine

def test_node_agent_allowlist_enforcement():
    agent = PrivilegedNodeAgent()

    # 1. Allowlisted action must succeed
    res = agent.dispatch("SYSTEMD_SERVICE_ACTION", {"unit": "test.service", "action": "restart"})
    assert res["status"] == "success"

    # 2. Arbitrary/unauthorized action must be blocked
    res_blocked = agent.dispatch("EXECUTE_RAW_SHELL", {"command": "rm -rf /"})
    assert res_blocked["status"] == "error"
    assert res_blocked["error"] == "UNAUTHORIZED_ACTION"

def test_policy_engine_validation():
    # Attempting to call unauthorized action on Node Agent client must raise PermissionError
    with pytest.raises(PermissionError) as exc_info:
        node_agent_client.execute_action("RUN_BASH_SCRIPT", {"script": "test.sh"})
    assert "not in the privileged allow-list" in str(exc_info.value)
