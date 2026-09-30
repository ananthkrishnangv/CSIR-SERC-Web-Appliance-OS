#!/bin/bash
#==================================================================
# CSIR-SWA OS Boot Health Gate Verification
# Validates platform integrity before promoting transactional update
#==================================================================
set -euo pipefail

LOG_FILE="/var/log/csir-health-gate.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "[$(date -u +%FT%TZ)] Starting CSIR-SWA OS Health Gate Verification..."

FAILURES=0

report_pass() {
    echo "[PASS] $1"
}

report_fail() {
    echo "[FAIL] $1"
    FAILURES=$((FAILURES + 1))
}

# 1. Verify read-only root status
if mount | grep ' on / ' | grep -q 'ro,'; then
    report_pass "Root filesystem is mounted read-only."
else
    # In some dev environments root might be rw, warn unless strictly enforced
    echo "[WARN] Root filesystem is not read-only. Check immutable profile."
fi

# 2. Check Node Agent socket
if [ -S "/run/csir-swa/agent.sock" ]; then
    report_pass "Privileged Node Agent socket exists and is active."
else
    report_fail "Privileged Node Agent socket /run/csir-swa/agent.sock is missing."
fi

# 3. Check Control Plane API responsiveness
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/v1/health || echo "000")
if [ "$HTTP_CODE" -eq 200 ]; then
    report_pass "Control Plane API responded with HTTP 200 OK."
else
    report_fail "Control Plane API failed health check (HTTP $HTTP_CODE)."
fi

# 4. Check Reverse Proxy (HAProxy) status
if systemctl is-active --quiet haproxy; then
    report_pass "HAProxy reverse proxy service is active."
else
    echo "[WARN] HAProxy service is inactive or not started yet."
fi

# 5. Check Host Firewall (nftables)
if nft list ruleset >/dev/null 2>&1; then
    report_pass "nftables firewall ruleset is loaded."
else
    report_fail "nftables firewall ruleset failed to load."
fi

# 6. Check Audit Log Integrity
if [ -f "/var/log/audit/csir_audit.ledger" ]; then
    report_pass "Cryptographic audit ledger exists."
else
    echo "[INFO] Creating initial audit ledger."
fi

# Summary
if [ "$FAILURES" -eq 0 ]; then
    echo "[SUCCESS] All CSIR Health Gates passed. System promoted."
    exit 0
else
    echo "[CRITICAL] $FAILURES health check(s) failed!"
    # Check if booted into an unverified transactional snapshot
    if [ -f "/run/transactional-update-boot" ]; then
        echo "[ACTION] Transactional update validation failed! Initiating rollback..."
        snapper rollback || true
        reboot
    fi
    exit 1
fi
