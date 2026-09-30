from typing import Tuple

class PolicyEngine:
    """OPA-aligned policy and safety guardrail engine for CSIR-SWA OS."""

    VALID_ROLES = {"admin", "security_officer", "operator", "auditor"}

    @classmethod
    def evaluate_ai_action_policy(cls, action_type: str, impact_level: str) -> Tuple[bool, str]:
        """
        Enforces Table 8.2 AI Action Class boundaries:
        - Low risk (rate limit, diagnostics) -> Can be automated
        - High impact (stop production, broad block) -> Human approval required
        - Critical (delete data, key rotation, failover) -> Dual approval required
        """
        if action_type in ["stop_workload", "broad_network_block"]:
            return False, "Action requires explicit Human Administrator approval."
        
        if action_type in ["delete_data", "rotate_critical_keys", "failover"]:
            return False, "Action requires Dual-Administrator approval."

        if impact_level in ["high", "critical"]:
            return False, "High or Critical impact operations must be signed off by a human administrator."

        return True, "Approved for automated execution under low-risk policy."

    @classmethod
    def validate_node_agent_action(cls, action_name: str, params: dict) -> Tuple[bool, str]:
        """
        Enforces Section 7.2:
        The Python service must never run unrestricted shell commands.
        Only strictly allow-listed typed operations can be dispatched.
        """
        ALLOWED_ACTIONS = {
            "SYSTEMD_SERVICE_ACTION",
            "SNAPPER_CREATE_SNAPSHOT",
            "SNAPPER_ROLLBACK",
            "RESTIC_RUN_BACKUP",
            "NFTABLES_APPLY_RULESET",
            "SUPPORT_BUNDLE_GENERATE",
            "QUADLET_GENERATE_UNIT",
            "CERT_ROTATE",
        }

        if action_name not in ALLOWED_ACTIONS:
            return False, f"Action '{action_name}' is not in the privileged allow-list. Execution blocked."

        # Safety check on service actions
        if action_name == "SYSTEMD_SERVICE_ACTION":
            unit = params.get("unit", "")
            action = params.get("action", "")
            if not unit.endswith((".service", ".timer", ".socket")):
                return False, f"Target unit '{unit}' is invalid."
            if action not in ["start", "stop", "restart", "reload", "status"]:
                return False, f"Systemd action '{action}' is not permitted."

        return True, "Action permitted by Node Agent policy."

policy_engine = PolicyEngine()
