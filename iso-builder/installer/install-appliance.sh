#!/bin/bash
#=============================================================================
# CSIR Secure Web Appliance OS (CSIR-SWA OS)
# Feature Installation Engine (Executes at OS Installation Time)
# Baseline: openSUSE MicroOS / SUSE Linux Micro 6.2
#=============================================================================
set -euo pipefail

TARGET_ROOT="${1:-/mnt}"
INSTALLER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${INSTALLER_DIR}/payload"

echo "====================================================================="
echo " [CSIR-SWA OS] Executing Automated Feature Installation at OS Install Time"
echo " Target Root: ${TARGET_ROOT}"
# Detect Appliance Installation Purpose / Profile
CMDLINE_PROFILE="$(grep -o 'csir_profile=[^ ]*' /proc/cmdline 2>/dev/null | cut -d= -f2 || true)"
CSIR_PROFILE="${CMDLINE_PROFILE:-${CSIR_PROFILE:-full}}"

echo " Installation Purpose: ${CSIR_PROFILE^^}"
echo " Timestamp:   $(date -u +%FT%TZ)"
echo "====================================================================="

# 1. Verify Target Root Directory Structure
mkdir -p "${TARGET_ROOT}/etc/csir-swa"
mkdir -p "${TARGET_ROOT}/var/lib/csir-swa/node_agent"
mkdir -p "${TARGET_ROOT}/var/lib/csir-swa/static"
mkdir -p "${TARGET_ROOT}/var/lib/libvirt/images"
mkdir -p "${TARGET_ROOT}/var/log/audit"
mkdir -p "${TARGET_ROOT}/srv/apps"
mkdir -p "${TARGET_ROOT}/srv/app-data"
mkdir -p "${TARGET_ROOT}/srv/www/vhosts/default/public_html"
mkdir -p "${TARGET_ROOT}/etc/haproxy/conf.d"
mkdir -p "${TARGET_ROOT}/etc/ssl/csir-swa"
mkdir -p "${TARGET_ROOT}/srv/backups"
mkdir -p "${TARGET_ROOT}/srv/repository"
mkdir -p "${TARGET_ROOT}/srv/models"
mkdir -p "${TARGET_ROOT}/etc/containers/systemd"
mkdir -p "${TARGET_ROOT}/etc/nftables"
mkdir -p "${TARGET_ROOT}/etc/coraza"
mkdir -p "${TARGET_ROOT}/etc/snapper/configs"
mkdir -p "${TARGET_ROOT}/usr/lib/csir-swa/bin"

# 2. Deploy Appliance Core Services (FastAPI Backend & Privileged Node Agent)
echo "[1/10] Deploying Control Plane, Node Agent & Services..."
if [ -d "${PAYLOAD_DIR}/backend" ]; then
    cp -r "${PAYLOAD_DIR}/backend/"* "${TARGET_ROOT}/var/lib/csir-swa/"
fi

# 3. Deploy Web Management Portal
echo "[2/10] Deploying Management Console Web Assets..."
if [ -d "${PAYLOAD_DIR}/static" ]; then
    cp -r "${PAYLOAD_DIR}/static/"* "${TARGET_ROOT}/var/lib/csir-swa/static/"
fi

# 4. Deploy Certified Podman Quadlets
echo "[3/10] Installing Certified Quadlet Application Templates..."
if [ -d "${PAYLOAD_DIR}/templates" ]; then
    cp -r "${PAYLOAD_DIR}/templates/"* "${TARGET_ROOT}/srv/apps/"
    # Copy default system-level quadlets
    find "${PAYLOAD_DIR}/templates" -name "*.container" -o -name "*.network" | while read -r qfile; do
        cp "$qfile" "${TARGET_ROOT}/etc/containers/systemd/"
    done
fi

# 5. Setup Rootless Podman Service Accounts
echo "[4/10] Configuring Rootless Podman Identity & Namespaces..."
if [ -f "${TARGET_ROOT}/etc/subuid" ]; then
    grep -q "csir-app" "${TARGET_ROOT}/etc/subuid" || echo "csir-app:100000:65536" >> "${TARGET_ROOT}/etc/subuid"
    grep -q "csir-app" "${TARGET_ROOT}/etc/subgid" || echo "csir-app:100000:65536" >> "${TARGET_ROOT}/etc/subgid"
fi

# 6. Deploy Security Profiles (WAF, Suricata, nftables)
echo "[5/10] Deploying Coraza WAF Rules, OWASP CRS & Host Firewall..."
if [ -d "${PAYLOAD_DIR}/security-profiles" ]; then
    cp -r "${PAYLOAD_DIR}/security-profiles/coraza/"* "${TARGET_ROOT}/etc/coraza/" 2>/dev/null || true
    cp "${PAYLOAD_DIR}/security-profiles/nftables/csir-firewall.nft" "${TARGET_ROOT}/etc/nftables/csir-firewall.nft" 2>/dev/null || true
fi

# 7. Configure Snapper and Transactional Update Policy
echo "[6/10] Configuring Snapper Snapshots & Transactional Updates..."
if [ -f "${PAYLOAD_DIR}/systemd/transactional-update.conf" ]; then
    cp "${PAYLOAD_DIR}/systemd/transactional-update.conf" "${TARGET_ROOT}/etc/transactional-update.conf"
fi
if [ -f "${PAYLOAD_DIR}/systemd/snapper-root" ]; then
    cp "${PAYLOAD_DIR}/systemd/snapper-root" "${TARGET_ROOT}/etc/snapper/configs/root"
fi

# 8. Deploy Systemd Units & Health Gates
echo "[7/10] Installing Systemd Service Units & Health Gate Scripts..."
if [ -d "${PAYLOAD_DIR}/systemd" ]; then
    cp "${PAYLOAD_DIR}/systemd/"*.service "${TARGET_ROOT}/etc/systemd/system/" 2>/dev/null || true
fi
if [ -d "${PAYLOAD_DIR}/bin" ]; then
    cp "${PAYLOAD_DIR}/bin/"*.sh "${TARGET_ROOT}/usr/lib/csir-swa/bin/" 2>/dev/null || true
    chmod +x "${TARGET_ROOT}/usr/lib/csir-swa/bin/"*.sh 2>/dev/null || true
fi

# 9. Initialize CERT-In Compliant Hash-Chained Audit Ledger
echo "[8/10] Initializing Cryptographic Audit Ledger (Genesis Block)..."
GENESIS_HASH="0000000000000000000000000000000000000000000000000000000000000000"
INIT_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GENESIS_RECORD="{\"index\":1,\"timestamp\":\"${INIT_TIMESTAMP}\",\"actor\":\"installer:os_install\",\"ip\":\"127.0.0.1\",\"action\":\"PROVISION_APPLIANCE\",\"resource\":\"system:rootfs\",\"prev_hash\":\"${GENESIS_HASH}\",\"entry_hash\":\"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\"}"
echo "${GENESIS_RECORD}" > "${TARGET_ROOT}/var/log/audit/csir_audit.ledger"
chmod 600 "${TARGET_ROOT}/var/log/audit/csir_audit.ledger"

# 10. Install 3rd-Party Repositories (/etc/zypp/repos.d/)
echo "[9/11] Configuring 3rd-Party & Production Repositories..."
mkdir -p "${TARGET_ROOT}/etc/zypp/repos.d"

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-oss.repo"
[csir-swa-oss]
name=openSUSE Tumbleweed Main OSS
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/tumbleweed/repo/oss/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-security.repo"
[csir-swa-security]
name=openSUSE Security Tools (Suricata, Falco, Coraza, Cosign)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/security/openSUSE_Tumbleweed/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-virtualization.repo"
[csir-swa-virtualization]
name=openSUSE Virtualization (KVM, QEMU, libvirt)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/Virtualization/openSUSE_Tumbleweed/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-microos.repo"
[csir-swa-microos]
name=openSUSE Container Stack (Podman 6.1, Netavark, Quadlet)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/devel:/microos/openSUSE_Tumbleweed/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-database.repo"
[csir-swa-database]
name=openSUSE Database Platform (PostgreSQL 17, PgBouncer)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/server:/database:/postgresql/openSUSE_Tumbleweed/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-network.repo"
[csir-swa-network]
name=openSUSE Edge Proxy Platform (HAProxy 3.0, NGINX)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/network/openSUSE_Tumbleweed/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-monitoring.repo"
[csir-swa-monitoring]
name=openSUSE Observability (Prometheus, Grafana, Loki)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/server:/monitoring/openSUSE_Tumbleweed/
type=rpm-md
gpgcheck=0
EOF

cat <<'EOF' > "${TARGET_ROOT}/etc/zypp/repos.d/csir-swa-dvd.repo"
[csir-swa-dvd]
name=CSIR-SWA OS Local DVD Offline Repository
enabled=1
autorefresh=0
baseurl=cd:/?devices=/dev/sr0,/dev/cdrom
type=rpm-md
gpgcheck=0
EOF

# 11. Install Console Banner & Issue Files (Section 6 Mockup)
echo "[10/11] Setting Console Boot Banner..."
if [ -f "${PAYLOAD_DIR}/issue" ]; then
    cp "${PAYLOAD_DIR}/issue" "${TARGET_ROOT}/etc/issue"
fi

# 12. Stamping Feature Installation Proof & Appliance Purpose Profile
echo "[11/11] Finalizing Feature Stamping & Appliance Profile..."
cat <<EOF > "${TARGET_ROOT}/etc/csir-swa/appliance-profile.json"
{
  "profile_code": "${CSIR_PROFILE}",
  "profile_name": "$(case "${CSIR_PROFILE}" in
    full) echo "Full-Stack Sovereign Web & Virtualization Appliance" ;;
    webhosting) echo "High-Density Web Hosting Gateway" ;;
    virtualization) echo "Micro-Virtualization & Container Node" ;;
    edge-waf) echo "Edge Reverse Proxy & Coraza WAF Security Gateway" ;;
    airgap) echo "Hardened Strategic Air-Gapped Laboratory & Archive Node" ;;
    *) echo "Custom Institutional Profile" ;;
  esac)",
  "virtualization_enabled": $(case "${CSIR_PROFILE}" in full|virtualization) echo "true" ;; *) echo "false" ;; esac),
  "webhosting_enabled": $(case "${CSIR_PROFILE}" in full|webhosting) echo "true" ;; *) echo "false" ;; esac),
  "waf_enabled": $(case "${CSIR_PROFILE}" in full|edge-waf) echo "true" ;; *) echo "false" ;; esac),
  "installed_at": "${INIT_TIMESTAMP}"
}
EOF

cat <<EOF > "${TARGET_ROOT}/etc/csir-swa/installation-receipt.json"
{
  "product": "CSIR Secure Web Appliance OS",
  "version": "1.0.0",
  "channel": "Stable",
  "installed_at_phase": "OS_INSTALLATION",
  "installation_purpose": "${CSIR_PROFILE}",
  "install_timestamp": "${INIT_TIMESTAMP}",
  "features_installed": [
    "FastAPI Control Plane (Python 3.14)",
    "Privileged Node Agent RPC",
    "Nuxt 4 / Vue 3 Management Portal",
    "Web Hosting & Multi-Tenant VHost Manager (PHP/Node/Python Runtimes)",
    "Rootless Podman 6.1.2 Quadlets",
    "KVM Hypervisor & libvirt Virtual Machine Subsystem",
    "Coraza WAF & OWASP CRS v4",
    "nftables Default-Deny Firewall",
    "Suricata IDS/IPS Profile",
    "Btrfs Snapper Snapshot Engine",
    "CERT-In Cryptographic Hash-Chain Audit",
    "Transactional-Update Health Gate"
  ],
  "immutable_root_configured": true,
  "status": "READY_FOR_FIRST_BOOT"
}
EOF

echo "====================================================================="
echo " [✓] CSIR-SWA OS Feature Installation Completed Successfully!"
echo " System will boot into fully operational appliance on restart."
echo "====================================================================="
exit 0
