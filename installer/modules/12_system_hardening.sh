#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 12: System Hardening & Compliance
# Implements CERT-In, CIS Benchmark sysctl, SSH, limits & institutional banners
#=============================================================================
set -euo pipefail

apply_system_hardening_and_compliance() {
    echo -e "${CYAN}[*] Applying OS Hardening, Security Baseline & Institutional Branding...${NC}"

    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # 1. Apply Kernel Sysctl Hardening
    echo -e "    • Deploying kernel hardening profile (/etc/sysctl.d/99-csir-security.conf)..."
    mkdir -p /etc/sysctl.d
    if [ -f "$SCRIPT_DIR/assets/security/99-csir-security.conf" ]; then
        cp "$SCRIPT_DIR/assets/security/99-csir-security.conf" /etc/sysctl.d/99-csir-security.conf
    fi
    sysctl --system >/dev/null 2>&1 || true

    # 2. Deploy Security Limits (File Descriptors & Process Limits)
    echo -e "    • Configuring process limits (/etc/security/limits.d/99-csir.conf)..."
    mkdir -p /etc/security/limits.d
    cat <<EOF > /etc/security/limits.d/99-csir.conf
*          soft    nofile     65536
*          hard    nofile     65536
*          soft    nproc      32768
*          hard    nproc      32768
*          hard    core       0
csir-app   soft    nofile     65536
csir-app   hard    nofile     65536
EOF

    # 3. Deploy Institutional Console Banners (/etc/issue, /etc/motd)
    echo -e "    • Installing CSIR-SERC institutional boot and login banners..."
    if [ -f "$SCRIPT_DIR/assets/branding/issue.banner" ]; then
        cp "$SCRIPT_DIR/assets/branding/issue.banner" /etc/issue
        cp "$SCRIPT_DIR/assets/branding/issue.banner" /etc/issue.net
    else
        cat <<'EOF' > /etc/issue
======================================================================
           CSIR-SERC SECURE WEB APPLIANCE OS (CSIR-SWA OS)
         Immutable Web, Application and Security Platform
======================================================================
  Management Console: https://\4:8443
  REST Control Plane: http://\4:8000/docs
  Authorised Personnel Only. All actions logged and audited.
======================================================================
EOF
        cp /etc/issue /etc/issue.net
    fi

    cat <<'EOF' > /etc/motd
======================================================================
  Welcome to CSIR-SERC Secure Web Appliance OS (Production Baseline)
  Unified Administration CLI: run 'csir-ctl status'
  Tamper-Evident Audit Ledger: run 'csir-ctl audit verify'
======================================================================
EOF

    # 4. SSH Server Hardening
    if [ -d /etc/ssh ]; then
        echo -e "    • Enforcing SSH hardening policy..."
        mkdir -p /etc/ssh/sshd_config.d
        cat <<EOF > /etc/ssh/sshd_config.d/99-csir-hardening.conf
PermitEmptyPasswords no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
X11Forwarding no
Banner /etc/issue.net
EOF
        systemctl reload sshd 2>/dev/null || systemctl reload ssh 2>/dev/null || true
    fi

    # 5. Configure NTP Time Synchronization (CERT-In Compliance)
    echo -e "    • Configuring NTP time synchronization with NPL India..."
    if [ -f /etc/chrony.conf ]; then
        if ! grep -q "time.nplindia.org" /etc/chrony.conf; then
            echo "server time.nplindia.org iburst" >> /etc/chrony.conf
            echo "server ntp.nic.in iburst" >> /etc/chrony.conf
            systemctl restart chronyd 2>/dev/null || true
        fi
    fi

    echo -e "${GREEN}[✓] System hardening and compliance policies enforced.${NC}"
}
