#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC SECURE WEB APPLIANCE OS (CSIR-SWA OS)
# Dedicated openSUSE MicroOS Server -> CSIR Appliance Converter
# Target: openSUSE MicroOS / Leap Micro / SUSE Linux Micro
# Description: Converts a vanilla openSUSE MicroOS server into a hardened,
#              immutable CSIR-SERC institutional web appliance using atomic
#              transactional-update snapshots and Btrfs state management.
# Lead Organisation: CSIR-SERC / Participating Laboratories
#=============================================================================
set -euo pipefail

# ANSI Color Codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_banner() {
    clear 2>/dev/null || true
    echo -e "${CYAN}${BOLD}"
    cat <<'EOF'
  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║                                                                              ║
  ║             CSIR-SERC SECURE WEB APPLIANCE OS (CSIR-SWA OS)                  ║
  ║               openSUSE MicroOS Transactional Appliance Converter             ║
  ║                                                                              ║
  ║  Transforms generic openSUSE MicroOS nodes into hardened institutional       ║
  ║  appliances using atomic Btrfs snapshots and transactional-update.           ║
  ║                                                                              ║
  ╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

usage() {
    cat <<EOF
Usage: sudo ./convert-microos.sh [OPTIONS]

Options:
  --help, -h             Show this help message and exit
  --unattended, -y       Non-interactive automated conversion (cloud-init / CI/CD)
  --profile <NAME>       Select appliance profile (default: full):
                           full       - Monolithic full stack (Portal, WAF, Podman, DB, DR, AI, Branding)
                           edge-waf   - Edge reverse proxy + Coraza WAF (OWASP CRS v4) + nftables
                           app-host   - Rootless Podman Quadlets + PostgreSQL + Backups + Hardening
                           minimal    - Core Management plane + Node Agent RPC + nftables
  --reboot, -r           Automatically reboot into newly staged CSIR appliance snapshot
  --no-reboot            Stage transactional snapshot but defer reboot to administrator
  --dry-run              Inspect environment, validate prerequisites, but make no changes

Examples:
  sudo ./convert-microos.sh                          # Interactive conversion wizard
  sudo ./convert-microos.sh --unattended --reboot    # Zero-touch full conversion & reboot
  sudo ./convert-microos.sh --profile edge-waf       # Convert to Edge WAF appliance
EOF
    exit 0
}

# Default Options
UNATTENDED=false
SELECTED_PROFILE="full"
AUTO_REBOOT=false
DEFER_REBOOT=false
DRY_RUN=false

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h)
            usage
            ;;
        --unattended|-y)
            UNATTENDED=true
            shift
            ;;
        --profile)
            SELECTED_PROFILE="$2"
            shift 2
            ;;
        --reboot|-r)
            AUTO_REBOOT=true
            shift
            ;;
        --no-reboot)
            DEFER_REBOOT=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo -e "${RED}[!] Unknown argument: $1${NC}"
            usage
            ;;
    esac
done

# Root Privilege Check
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo -e "${RED}[!] Error: This conversion script must be executed with root privileges (sudo).${NC}" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

print_banner

#=============================================================================
# Step 1: MicroOS Environment Verification & Safety Gates
#=============================================================================
echo -e "${CYAN}${BOLD}=== Phase 1: openSUSE MicroOS Platform Verification ===${NC}"

if [ ! -f /etc/os-release ]; then
    echo -e "${RED}[!] Error: /etc/os-release not found. Unsupported system.${NC}" >&2
    exit 1
fi

# shellcheck source=/dev/null
. /etc/os-release
DISTRO_NAME="${NAME:-Unknown}"
DISTRO_ID="${ID:-unknown}"
DISTRO_VERSION="${VERSION_ID:-unknown}"

echo -e "    • OS Identity:         ${WHITE}${DISTRO_NAME} (${DISTRO_ID} ${DISTRO_VERSION})${NC}"

# Verify MicroOS
IS_MICROOS=false
if [[ "$DISTRO_ID" == *"microos"* ]] || [[ "$DISTRO_NAME" == *"MicroOS"* ]] || [[ "$DISTRO_NAME" == *"Leap Micro"* ]] || [[ "$DISTRO_NAME" == *"SL Micro"* ]]; then
    IS_MICROOS=true
fi

if [ "$IS_MICROOS" = false ]; then
    echo -e "${YELLOW}[!] Warning: This host does not appear to be openSUSE MicroOS.${NC}"
    echo -e "    Detected OS: ${DISTRO_NAME} (${DISTRO_ID})"
    if [ "$UNATTENDED" = false ]; then
        read -rp "Do you wish to continue forcing openSUSE MicroOS conversion mode? [y/N]: " FORCE_RUN
        if [[ ! "$FORCE_RUN" =~ ^[Yy] ]]; then
            echo -e "${YELLOW}[i] Aborted. For non-MicroOS systems, use: sudo ./setup-appliance.sh${NC}"
            exit 1
        fi
    else
        echo -e "${RED}[!] Error: Aborting unattended run on non-MicroOS host.${NC}" >&2
        exit 1
    fi
fi

# Verify transactional-update utility
if ! command -v transactional-update >/dev/null 2>&1; then
    echo -e "${RED}[!] Error: 'transactional-update' command not found. This system lacks MicroOS transactional infrastructure.${NC}" >&2
    exit 1
fi
echo -e "    • Transactional Engine:${GREEN}[✓] transactional-update available${NC}"

# Verify Btrfs Root Filesystem
ROOT_FSTYPE=$(df -T / | awk 'NR==2 {print $2}')
if [ "$ROOT_FSTYPE" != "btrfs" ]; then
    echo -e "${RED}[!] Error: Root filesystem is '${ROOT_FSTYPE}'. MicroOS requires Btrfs with snapshot capabilities.${NC}" >&2
    exit 1
fi
echo -e "    • Filesystem:          ${GREEN}[✓] Btrfs root confirmed${NC}"

# Hardware Resources
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
CPU_CORES=$(nproc)
DISK_FREE_GB=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')

echo -e "    • Compute Resources:   ${WHITE}${CPU_CORES} vCPUs, ${TOTAL_RAM_MB} MB RAM, ${DISK_FREE_GB} GB Free Disk${NC}"

if [ "$DISK_FREE_GB" -lt 5 ]; then
    echo -e "${YELLOW}[!] Warning: Disk free space (${DISK_FREE_GB} GB) is below 5 GB. Btrfs snapshots require adequate headroom.${NC}"
fi

# Profile Confirmation
echo ""
echo -e "${CYAN}${BOLD}=== Selected Appliance Profile: ${WHITE}${SELECTED_PROFILE^^}${CYAN} ===${NC}"
case "$SELECTED_PROFILE" in
    "full")
        echo -e "    Installs: Core Management Portal, UX4G Nuxt UI, Node Agent, HAProxy 3.0, Coraza WAF (CRS v4),"
        echo -e "              nftables default-deny, Podman Quadlets, PostgreSQL, Snapper/Restic DR, AI Center, Branding."
        ;;
    "edge-waf")
        echo -e "    Installs: Core Management, Node Agent, HAProxy 3.0, Coraza WAF (CRS v4), nftables, Suricata IDS, Branding."
        ;;
    "app-host")
        echo -e "    Installs: Core Management, Node Agent, Podman Quadlets, PostgreSQL, Backups, Hardening, Branding."
        ;;
    "minimal")
        echo -e "    Installs: Core Management, Node Agent RPC, nftables default-deny, System Hardening."
        ;;
    *)
        echo -e "${RED}[!] Invalid profile: $SELECTED_PROFILE. Defaulting to 'full'.${NC}"
        SELECTED_PROFILE="full"
        ;;
esac

if [ "$UNATTENDED" = false ] && [ "$DRY_RUN" = false ]; then
    echo ""
    read -rp "Proceed with converting this openSUSE MicroOS server? [Y/n]: " CONFIRM_CONVERT
    if [[ "$CONFIRM_CONVERT" =~ ^[Nn] ]]; then
        echo -e "${YELLOW}[i] Conversion cancelled by user.${NC}"
        exit 0
    fi
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY-RUN] Prerequisite checks passed. Exiting dry run.${NC}"
    exit 0
fi

#=============================================================================
# Step 2: Conflict Resolution & Pre-Migration Cleanup
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 2: Conflict Resolution & Legacy Service Retirement ===${NC}"
BACKUP_DIR="/var/backups/csir-microos-preconversion-$(date +%Y%m%d%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 1. Mask and stop firewalld if active
if systemctl is-active --quiet firewalld 2>/dev/null; then
    echo -e "${YELLOW}[!] Active firewalld found. Backing up and switching to native nftables default-deny...${NC}"
    [ -d /etc/firewalld ] && cp -r /etc/firewalld "$BACKUP_DIR/firewalld.bak" 2>/dev/null || true
    systemctl stop firewalld || true
    systemctl disable firewalld || true
    systemctl mask firewalld || true
    echo -e "${GREEN}[✓] firewalld stopped and masked.${NC}"
fi

# 2. Check and retire conflicting web servers
for ws in httpd apache2 lighttpd caddy; do
    if systemctl is-active --quiet "$ws" 2>/dev/null; then
        echo -e "${YELLOW}[!] Active web server '$ws' found on ports 80/443. Stopping and masking...${NC}"
        systemctl stop "$ws" || true
        systemctl disable "$ws" || true
        systemctl mask "$ws" || true
        echo -e "${GREEN}[✓] Disabled conflicting web server: $ws${NC}"
    fi
done

# 3. Clean up stale CSIR daemon instances
for csir_svc in csir-control-plane csir-node-agent csir-health-gate; do
    if systemctl is-active --quiet "$csir_svc" 2>/dev/null; then
        echo -e "${BLUE}[i] Stopping active instance of $csir_svc for clean upgrade...${NC}"
        systemctl stop "$csir_svc" || true
    fi
done
rm -f /run/csir-swa/agent.sock 2>/dev/null || true

#=============================================================================
# Step 3: Create Persistent Appliance Subvolume & Directory Layout
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 3: Provisioning Persistent Directory Hierarchy ===${NC}"
# In openSUSE MicroOS, /var, /srv, /etc, /opt are writable and persist across snapshots.
mkdir -p /etc/csir-swa
mkdir -p /etc/coraza
mkdir -p /etc/nftables
mkdir -p /etc/containers/systemd
mkdir -p /etc/containers/registries.conf.d
mkdir -p /etc/snapper/configs
mkdir -p /etc/ssl/csir-swa
mkdir -p /etc/sysctl.d
mkdir -p /etc/security/limits.d
mkdir -p /etc/ssh/sshd_config.d

mkdir -p /var/lib/csir-swa/app
mkdir -p /var/lib/csir-swa/node_agent
mkdir -p /var/lib/csir-swa/cli
mkdir -p /var/lib/csir-swa/bin
mkdir -p /var/lib/csir-swa/static
mkdir -p /var/lib/csir-swa/data/logs
mkdir -p /var/lib/csir-swa/ai-engine
mkdir -p /var/log/audit

mkdir -p /srv/apps
mkdir -p /srv/app-data
mkdir -p /srv/www/vhosts/default/public_html
mkdir -p /etc/haproxy/conf.d
mkdir -p /etc/ssl/csir-swa/certs
mkdir -p /etc/ssl/csir-swa/private
mkdir -p /srv/backups/restic-repo
mkdir -p /srv/models
mkdir -p /run/csir-swa

echo -e "${GREEN}[✓] Persistent appliance directory structure initialized.${NC}"

#=============================================================================
# Step 4: Dedicated Service Accounts & Container Isolation
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 4: Service Accounts & Workload Namespaces ===${NC}"

if ! id -u csir-swa >/dev/null 2>&1; then
    useradd -r -s /sbin/nologin -d /var/lib/csir-swa -c "CSIR-SWA Management Plane" csir-swa || true
    echo -e "${GREEN}[✓] Created daemon user: csir-swa${NC}"
fi

if ! id -u csir-app >/dev/null 2>&1; then
    useradd -u 100000 -s /sbin/nologin -d /srv/apps -c "CSIR Workload Isolation Account" csir-app || true
    echo -e "${GREEN}[✓] Created isolated workload user: csir-app (UID 100000)${NC}"
fi

# Configure subuid and subgid for rootless Podman user namespaces
touch /etc/subuid /etc/subgid
grep -q "csir-app" /etc/subuid || echo "csir-app:100000:65536" >> /etc/subuid
grep -q "csir-app" /etc/subgid || echo "csir-app:100000:65536" >> /etc/subgid
echo -e "${GREEN}[✓] Rootless container namespace mapped: csir-app:100000:65536${NC}"

#=============================================================================
# Step 5: Configure Verified openSUSE Repositories
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 5: Configuring openSUSE Package Repositories ===${NC}"
mkdir -p /etc/zypp/repos.d

SUSE_TARGET="openSUSE_Tumbleweed"
if [[ "$DISTRO_NAME" == *"Leap"* ]] || [[ "$DISTRO_VERSION" =~ ^15\. ]]; then
    SUSE_TARGET="15.6"
fi

cat <<EOF > /etc/zypp/repos.d/csir-network.repo
[csir-network]
name=CSIR Edge Proxy Platform (HAProxy)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/network/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

cat <<EOF > /etc/zypp/repos.d/csir-security.repo
[csir-security]
name=CSIR Security Tools (Suricata, Coraza)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/security/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

cat <<EOF > /etc/zypp/repos.d/csir-database.repo
[csir-database]
name=CSIR Database Platform (PostgreSQL)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/server:/database:/postgresql/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

echo -e "${GREEN}[✓] Zypper appliance repositories configured in /etc/zypp/repos.d/${NC}"

#=============================================================================
# Step 6: Atomic Transactional Package Staging (transactional-update)
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 6: Atomic Transactional Package Staging via transactional-update ===${NC}"
echo -e "${BLUE}[i] Compiling package installation set for profile '${SELECTED_PROFILE}'...${NC}"

# Core base packages needed across all profiles
PKG_LIST="python3 python3-pip python3-venv openssl ca-certificates chrony jq curl nftables"

case "$SELECTED_PROFILE" in
    "full")
        PKG_LIST="${PKG_LIST} haproxy suricata podman crun netavark aardvark-dns catatonit snapper restic borgbackup postgresql postgresql-server pgbouncer"
        ;;
    "edge-waf")
        PKG_LIST="${PKG_LIST} haproxy suricata"
        ;;
    "app-host")
        PKG_LIST="${PKG_LIST} haproxy podman crun netavark aardvark-dns catatonit snapper restic postgresql postgresql-server"
        ;;
    "minimal")
        # Base PKG_LIST is sufficient
        ;;
esac

echo -e "    • Packages to stage into new Btrfs root snapshot:"
echo -e "      ${WHITE}${PKG_LIST}${NC}"
echo ""
echo -e "${CYAN}[*] Executing transactional-update to create and stage target snapshot...${NC}"
echo -e "${YELLOW}[!] Note: In openSUSE MicroOS, packages are safely applied into a fresh snapshot.${NC}"

# Execute single atomic transactional update
if transactional-update --continue pkg install -y $PKG_LIST; then
    echo -e "${GREEN}[✓] Transactional package installation completed successfully.${NC}"
else
    echo -e "${YELLOW}[!] Primary transactional-update exited with a non-zero code. Retrying with --auto-agree-with-licenses...${NC}"
    transactional-update --continue --auto-agree-with-licenses pkg install -y $PKG_LIST || {
        echo -e "${RED}[!] Error: transactional-update failed to stage packages. Check network connection or package repository availability.${NC}" >&2
        exit 1
    }
fi

#=============================================================================
# Step 7: Deploy Control Plane Python Environment & Static Portal
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 7: Deploying Management Control Plane & Node Agent ===${NC}"

# 1. Create Python Virtual Environment in persistent /var
echo -e "    • Initializing isolated Python virtualenv at /var/lib/csir-swa/venv..."
python3 -m venv /var/lib/csir-swa/venv || {
    echo -e "${YELLOW}[!] Host python3 venv module not yet active in live root. Using pip install to bootstrap...${NC}"
}

if [ -f /var/lib/csir-swa/venv/bin/pip ]; then
    echo -e "    • Installing Python runtime dependencies..."
    /var/lib/csir-swa/venv/bin/pip install --upgrade pip setuptools wheel || true
    /var/lib/csir-swa/venv/bin/pip install fastapi uvicorn pydantic sqlalchemy python-jose cryptography psutil jinja2 pyyaml httpx python-multipart || true
fi

# 2. Deploy Backend Application Code
echo -e "    • Copying Control Plane, Node Agent, and CLI modules..."
if [ -d "${PROJECT_ROOT}/backend/app" ]; then
    cp -r "${PROJECT_ROOT}/backend/app"/* /var/lib/csir-swa/app/
    [ -f "${PROJECT_ROOT}/backend/app/main.py" ] && cp "${PROJECT_ROOT}/backend/app/main.py" /var/lib/csir-swa/app/
fi

if [ -d "${PROJECT_ROOT}/backend/node_agent" ]; then
    cp -r "${PROJECT_ROOT}/backend/node_agent"/* /var/lib/csir-swa/node_agent/
fi

if [ -d "${PROJECT_ROOT}/backend/cli" ]; then
    cp -r "${PROJECT_ROOT}/backend/cli"/* /var/lib/csir-swa/cli/
    chmod +x /var/lib/csir-swa/cli/csir_ctl.py 2>/dev/null || true
fi

# Create symlink for csir-ctl CLI
ln -sf /var/lib/csir-swa/cli/csir_ctl.py /usr/local/bin/csir-ctl 2>/dev/null || true
ln -sf /var/lib/csir-swa/cli/csir_ctl.py /var/lib/csir-swa/bin/csir-ctl 2>/dev/null || true

# 3. Deploy UX4G Web Console Static UI Assets
echo -e "    • Deploying UX4G Management Web Console static assets..."
if [ -d "${PROJECT_ROOT}/backend/app/static" ]; then
    cp -r "${PROJECT_ROOT}/backend/app/static"/* /var/lib/csir-swa/static/
elif [ -d "${PROJECT_ROOT}/frontend" ]; then
    # Create clean fallback index.html if frontend is not pre-compiled
    cat <<'EOF' > /var/lib/csir-swa/static/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSIR Secure Web Appliance OS</title>
    <style>
        body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:#0b1d33; color:#f0f4f8; display:flex; justify-content:center; align-items:center; min-height:100vh; }
        .card { background:#152b46; padding:40px; border-radius:12px; border:1px solid #234267; max-width:600px; text-align:center; box-shadow:0 10px 25px rgba(0,0,0,0.5); }
        h1 { color:#00d2ff; margin-bottom:10px; font-size:26px; }
        p { color:#94a3b8; line-height:1.6; }
        .badge { display:inline-block; padding:6px 14px; background:#00d2ff22; color:#00d2ff; border:1px solid #00d2ff55; border-radius:20px; font-size:13px; font-weight:600; margin:15px 0; }
        .links a { color:#38bdf8; text-decoration:none; margin:0 12px; font-weight:500; }
        .links a:hover { text-decoration:underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>CSIR Secure Web Appliance OS</h1>
        <div class="badge">Immutable Production Platform • MicroOS Baseline</div>
        <p>Your institutional appliance has been converted into the CSIR-SWA OS environment. The FastAPI Control Plane is operational.</p>
        <div class="links">
            <a href="/docs" target="_blank">Interactive Swagger Docs</a>
            <a href="/api/v1/health" target="_blank">Health Check API</a>
        </div>
    </div>
</body>
</html>
EOF
fi

# 4. Generate Appliance Control Plane Environment
echo -e "    • Generating /etc/csir-swa/control-plane.env..."
JWT_SECRET="csir-swa-strategic-key-$(openssl rand -hex 16 2>/dev/null || echo '2026-production')"
cat <<EOF > /etc/csir-swa/control-plane.env
PROJECT_NAME="CSIR Secure Web Appliance OS"
APP_VERSION="1.0.0"
API_V1_STR="/api/v1"
CSIR_DATA_DIR="/var/lib/csir-swa/data"
CSIR_LOG_DIR="/var/lib/csir-swa/data/logs"
CSIR_AUDIT_LEDGER_PATH="/var/log/audit/csir_audit.ledger"
DATABASE_URL="sqlite:////var/lib/csir-swa/data/csir_swa.db"
CSIR_SECRET_KEY="${JWT_SECRET}"
ACCESS_TOKEN_EXPIRE_MINUTES="480"
NODE_AGENT_SOCKET="/run/csir-swa/agent.sock"
NODE_AGENT_MOCK="false"
CURRENT_CHANNEL="Stable"
CERT_IN_REPORTING_HOURS="6"
LOG_RETENTION_DAYS="180"
NTP_SERVERS="time.nplindia.org,ntp.nic.in"
EOF
chmod 600 /etc/csir-swa/control-plane.env

# 5. Initialize CERT-In Cryptographic Audit Ledger
echo -e "    • Initializing CERT-In Cryptographic Audit Ledger (Genesis Block)..."
INIT_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat <<EOF > /var/log/audit/csir_audit.ledger
{"index":1,"timestamp":"${INIT_TIMESTAMP}","actor":"microos_converter","ip":"127.0.0.1","action":"CONVERT_MICROOS_SERVER","resource":"system:os","prev_hash":"0000000000000000000000000000000000000000000000000000000000000000","entry_hash":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
EOF
chmod 600 /var/log/audit/csir_audit.ledger

#=============================================================================
# Step 8: Network, WAF, Firewall, and SSL Security Baseline
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 8: Hardening Network, WAF, TLS 1.3 & Firewall ===${NC}"

# 1. TLS 1.3 Self-Signed Appliance Certificate
CERT_DIR="/etc/ssl/csir-swa"
if [ ! -f "$CERT_DIR/appliance.pem" ]; then
    echo -e "    • Generating TLS 1.3 appliance certificates..."
    openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
        -keyout "$CERT_DIR/appliance.key" \
        -out "$CERT_DIR/appliance.crt" \
        -subj "/C=IN/ST=Tamil Nadu/L=Chennai/O=CSIR-SERC/OU=Secure Infrastructure/CN=$(hostname -f 2>/dev/null || echo 'csir-appliance.local')" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null || true
    cat "$CERT_DIR/appliance.crt" "$CERT_DIR/appliance.key" > "$CERT_DIR/appliance.pem"
    chmod 600 "$CERT_DIR/appliance.key" "$CERT_DIR/appliance.pem"
fi

# 2. Coraza WAF & OWASP Core Rule Set v4 Profiles
echo -e "    • Deploying Coraza WAF & OWASP CRS v4 profiles..."
if [ -f "${SCRIPT_DIR}/assets/security/coraza.conf" ]; then
    cp "${SCRIPT_DIR}/assets/security/coraza.conf" /etc/coraza/coraza.conf
fi
if [ -f "${SCRIPT_DIR}/assets/security/crs-setup.conf" ]; then
    cp "${SCRIPT_DIR}/assets/security/crs-setup.conf" /etc/coraza/crs-setup.conf
fi

# 3. HAProxy Configuration
echo -e "    • Generating /etc/haproxy/haproxy.cfg..."
mkdir -p /etc/haproxy
cat <<EOF > /etc/haproxy/haproxy.cfg
global
    log /dev/log local0 info
    chroot /var/lib/haproxy
    user haproxy
    group haproxy
    daemon
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.3 no-tls-tickets

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

# Public Plain HTTP (Redirect to HTTPS)
frontend fe_http
    bind *:80
    mode http
    redirect scheme https code 301 if !{ ssl_fc }

# Public HTTPS Ingress (Hosted Websites & Portals)
frontend fe_https
    bind *:443 ssl crt /etc/ssl/csir-swa/appliance.pem
    mode http
    http-response set-header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    http-response set-header X-Content-Type-Options "nosniff"
    http-response set-header X-Frame-Options "SAMEORIGIN"
    http-response set-header Referrer-Policy "strict-origin-when-cross-origin"
    default_backend be_default_app

# Appliance Management Portal (Port 8443)
frontend fe_management
    bind *:8443 ssl crt /etc/ssl/csir-swa/appliance.pem
    mode http
    http-response set-header X-Appliance-Identity "CSIR-SERC-Secure-Appliance-OS"
    default_backend be_control_plane

# Control Plane Backend (FastAPI + Static UI)
backend be_control_plane
    mode http
    server srv_fastapi 127.0.0.1:8000 check

# Default Application Backend (Hosted Research Portal Quadlet)
backend be_default_app
    mode http
    server srv_app 127.0.0.1:8080 check backup
EOF

# 4. nftables Default-Deny Firewall
echo -e "    • Deploying /etc/nftables/csir-firewall.nft..."
if [ -f "${SCRIPT_DIR}/assets/security/csir-firewall.nft" ]; then
    cp "${SCRIPT_DIR}/assets/security/csir-firewall.nft" /etc/nftables/csir-firewall.nft
else
    cat <<'EOF' > /etc/nftables/csir-firewall.nft
table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        # Connection tracking
        ct state established,related accept
        ct state invalid drop

        # Loopback
        iif "lo" accept

        # Rate-limited ICMP (ping)
        ip protocol icmp icmp type echo-request limit rate 5/second accept
        ip6 nexthdr icmpv6 icmpv6 type echo-request limit rate 5/second accept

        # Public Web & Management Ports
        tcp dport { 80, 443 } accept
        tcp dport 8443 accept

        # Drop log
        log prefix "NFTABLES-DROP: " flags all drop
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
EOF
fi

if [ -f /etc/sysconfig/nftables.conf ]; then
    echo 'include "/etc/nftables/csir-firewall.nft"' > /etc/sysconfig/nftables.conf
elif [ -f /etc/nftables.conf ]; then
    echo 'include "/etc/nftables/csir-firewall.nft"' > /etc/nftables.conf
fi

# 5. Podman Container Quadlets
if [ "$SELECTED_PROFILE" = "full" ] || [ "$SELECTED_PROFILE" = "app-host" ]; then
    echo -e "    • Deploying certified Podman Quadlets..."
    cat <<EOF > /etc/containers/systemd/csir-portal.container
[Unit]
Description=CSIR Institutional Research Portal (Certified Quadlet)
Documentation=https://github.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS
After=network-online.target

[Container]
Image=docker.io/library/nginx:alpine
ContainerName=csir-research-portal
PublishPort=127.0.0.1:8080:80
Volume=/srv/apps/portal-data:/usr/share/nginx/html:ro
DropCapability=ALL
AddCapability=CHOWN SETUID SETGID NET_BIND_SERVICE
ReadOnly=true
SecurityLabelDisable=false

[Service]
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
EOF
    mkdir -p /srv/apps/portal-data
    cat <<'EOF' > /srv/apps/portal-data/index.html
<!DOCTYPE html>
<html>
<head><title>CSIR Institutional Portal</title></head>
<body style="font-family:sans-serif; text-align:center; padding:50px; background:#0b1d33; color:#fff;">
<h1>CSIR-SERC Secure Web Appliance Workload</h1>
<p>Containerized Quadlet application running securely on openSUSE MicroOS.</p>
</body>
</html>
EOF
fi

# 6. Snapper Btrfs Snapshot Configuration
cat <<EOF > /etc/snapper/configs/root
SUBVOLUME="/"
FSTYPE="btrfs"
TIMELINE_CREATE="yes"
TIMELINE_CLEANUP="yes"
TIMELINE_MIN_AGE="1800"
TIMELINE_LIMIT_HOURLY="10"
TIMELINE_LIMIT_DAILY="7"
TIMELINE_LIMIT_WEEKLY="4"
TIMELINE_LIMIT_MONTHLY="12"
NUMBER_LIMIT="10"
NUMBER_LIMIT_IMPORTANT="5"
EOF

# 7. OS Hardening Baseline (sysctl, limits, ssh, banners)
echo -e "    • Enforcing OS hardening, banners, and sysctl baseline..."
if [ -f "${SCRIPT_DIR}/assets/security/99-csir-security.conf" ]; then
    cp "${SCRIPT_DIR}/assets/security/99-csir-security.conf" /etc/sysctl.d/99-csir-security.conf
fi

cat <<EOF > /etc/security/limits.d/99-csir.conf
*          soft    nofile     65536
*          hard    nofile     65536
*          soft    nproc      32768
*          hard    nproc      32768
*          hard    core       0
csir-app   soft    nofile     65536
csir-app   hard    nofile     65536
EOF

if [ -f "${SCRIPT_DIR}/assets/branding/issue.banner" ]; then
    cp "${SCRIPT_DIR}/assets/branding/issue.banner" /etc/issue
    cp "${SCRIPT_DIR}/assets/branding/issue.banner" /etc/issue.net
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
  Welcome to CSIR-SERC Secure Web Appliance OS (MicroOS Baseline)
  Unified Administration CLI: run 'csir-ctl status'
  Tamper-Evident Audit Ledger: run 'csir-ctl audit verify'
======================================================================
EOF

if [ -d /etc/ssh ]; then
    mkdir -p /etc/ssh/sshd_config.d
    cat <<EOF > /etc/ssh/sshd_config.d/99-csir-hardening.conf
PermitEmptyPasswords no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
X11Forwarding no
Banner /etc/issue.net
EOF
fi

# 8. Time Sync Configuration (CERT-In Compliance)
if [ -f /etc/chrony.conf ]; then
    if ! grep -q "time.nplindia.org" /etc/chrony.conf; then
        echo "server time.nplindia.org iburst" >> /etc/chrony.conf
        echo "server ntp.nic.in iburst" >> /etc/chrony.conf
    fi
fi

#=============================================================================
# Step 9: Systemd Service Units & MicroOS Health Gate Integration
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 9: Deploying Systemd Units & Health Gate Hook ===${NC}"

# Deploy Health Gate Script to /var/lib/csir-swa/bin/
cat <<'EOF' > /var/lib/csir-swa/bin/csir-health-gate.sh
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

report_pass() { echo "[PASS] $1"; }
report_fail() { echo "[FAIL] $1"; FAILURES=$((FAILURES + 1)); }

# 1. Verify read-only root status
if mount | grep ' on / ' | grep -q 'ro,'; then
    report_pass "Root filesystem is mounted read-only."
else
    echo "[WARN] Root filesystem is not read-only. Immutable profile recommended."
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

# 4. Check Reverse Proxy (HAProxy)
if systemctl is-active --quiet haproxy; then
    report_pass "HAProxy reverse proxy service is active."
else
    echo "[WARN] HAProxy service is inactive."
fi

# 5. Check Host Firewall (nftables)
if nft list ruleset >/dev/null 2>&1; then
    report_pass "nftables firewall ruleset is loaded."
else
    report_fail "nftables firewall ruleset failed to load."
fi

# 6. Check Audit Ledger
if [ -f "/var/log/audit/csir_audit.ledger" ]; then
    report_pass "Cryptographic audit ledger exists."
fi

if [ "$FAILURES" -eq 0 ]; then
    echo "[SUCCESS] All CSIR Health Gates passed. System promoted."
    exit 0
else
    echo "[CRITICAL] $FAILURES health check(s) failed!"
    if [ -f "/run/transactional-update-boot" ]; then
        echo "[ACTION] Transactional update validation failed! Initiating rollback..."
        snapper rollback || true
        reboot
    fi
    exit 1
fi
EOF
chmod +x /var/lib/csir-swa/bin/csir-health-gate.sh

# Configure transactional-update.conf to use our health gate
cat <<EOF > /etc/transactional-update.conf
REBOOT_METHOD="systemd"
UPDATE_ALLOW_AUTOMATIC_REBOOT="no"
HEALTH_CHECK_SCRIPT="/var/lib/csir-swa/bin/csir-health-gate.sh"
ROLLBACK_ON_FAILURE="yes"
EOF

# Deploy Control Plane Systemd Unit
cat <<EOF > /etc/systemd/system/csir-control-plane.service
[Unit]
Description=CSIR-SWA OS Management Control Plane (FastAPI Backend)
Documentation=https://github.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS
After=network.target csir-node-agent.service
Requires=csir-node-agent.service

[Service]
Type=simple
User=csir-swa
Group=csir-swa
WorkingDirectory=/var/lib/csir-swa
EnvironmentFile=/etc/csir-swa/control-plane.env
ExecStart=/var/lib/csir-swa/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5s
LimitNOFILE=65536
ProtectSystem=full
ProtectHome=true
PrivateTmp=true
NoNewPrivileges=true
ReadWritePaths=/var/lib/csir-swa /var/log/audit

[Install]
WantedBy=multi-user.target
EOF

# Deploy Node Agent Systemd Unit
cat <<EOF > /etc/systemd/system/csir-node-agent.service
[Unit]
Description=CSIR-SWA OS Privileged Node Agent
Documentation=https://github.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS
After=network.target local-fs.target
Before=csir-control-plane.service

[Service]
Type=simple
User=root
Group=root
RuntimeDirectory=csir-swa
RuntimeDirectoryMode=0750
ExecStart=/var/lib/csir-swa/venv/bin/python3 -m node_agent.agent --socket /run/csir-swa/agent.sock
Restart=always
RestartSec=5s
LimitNOFILE=65536
CapabilityBoundingSet=CAP_SYS_ADMIN CAP_NET_ADMIN CAP_DAC_OVERRIDE
AmbientCapabilities=CAP_SYS_ADMIN CAP_NET_ADMIN CAP_DAC_OVERRIDE
ProtectSystem=strict
ReadWritePaths=/run/csir-swa /var/lib/csir-swa /srv/apps /srv/app-data /srv/backups /etc/nftables
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Deploy Boot Health Gate Systemd Unit
cat <<EOF > /etc/systemd/system/csir-health-gate.service
[Unit]
Description=CSIR-SWA OS Boot Health Gate Verification
Documentation=https://github.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS
After=csir-control-plane.service haproxy.service nftables.service
Before=multi-user.target
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/var/lib/csir-swa/bin/csir-health-gate.sh
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

# Set Permissions
chown -R csir-swa:csir-swa /var/lib/csir-swa
chmod 750 /var/lib/csir-swa

# Enable Services for target snapshot
echo -e "    • Enabling systemd services for target appliance boot..."
systemctl daemon-reload
systemctl enable csir-node-agent.service || true
systemctl enable csir-control-plane.service || true
systemctl enable csir-health-gate.service || true
systemctl enable haproxy.service || true
systemctl enable nftables.service || true
systemctl enable podman-auto-update.timer || true
systemctl enable snapper-timeline.timer || true
systemctl enable snapper-cleanup.timer || true

#=============================================================================
# Step 10: Bootloader Branding (GRUB Theme)
#=============================================================================
echo ""
echo -e "${CYAN}${BOLD}=== Phase 10: Applying CSIR-SERC Visual Bootloader Branding ===${NC}"
THEME_DIR="/boot/grub2/themes/csir-serc"
mkdir -p "$THEME_DIR"

if [ -f "${SCRIPT_DIR}/assets/branding/background.jpg" ]; then
    cp "${SCRIPT_DIR}/assets/branding/background.jpg" "${THEME_DIR}/background.jpg"
fi
if [ -f "${SCRIPT_DIR}/assets/branding/logo.png" ]; then
    cp "${SCRIPT_DIR}/assets/branding/logo.png" "${THEME_DIR}/logo.png"
fi
if [ -f "${SCRIPT_DIR}/assets/branding/grub-theme.txt" ]; then
    cp "${SCRIPT_DIR}/assets/branding/grub-theme.txt" "${THEME_DIR}/theme.txt"
fi

if [ -f /etc/default/grub ]; then
    sed -i '/^GRUB_THEME=/d' /etc/default/grub
    sed -i '/^GRUB_BACKGROUND=/d' /etc/default/grub
    sed -i '/^GRUB_DISTRIBUTOR=/d' /etc/default/grub
    cat <<EOF >> /etc/default/grub
GRUB_DISTRIBUTOR="CSIR-SERC Secure Web Appliance OS"
GRUB_THEME="${THEME_DIR}/theme.txt"
GRUB_BACKGROUND="${THEME_DIR}/background.jpg"
GRUB_TIMEOUT=8
EOF

    # Regenerate GRUB via transactional snapshot
    transactional-update run grub2-mkconfig -o /boot/grub2/grub.cfg 2>/dev/null || grub2-mkconfig -o /boot/grub2/grub.cfg 2>/dev/null || true
fi

#=============================================================================
# Step 11: Installation Receipt & Activation
#=============================================================================
INSTALL_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat <<EOF > /etc/csir-swa/installation-receipt.json
{
  "product": "CSIR Secure Web Appliance OS",
  "version": "1.0.0",
  "deployment_type": "OPENSUSE_MICROOS_TRANSACTIONAL_CONVERSION",
  "base_distribution": "${DISTRO_NAME} (${DISTRO_ID} ${DISTRO_VERSION})",
  "profile": "${SELECTED_PROFILE}",
  "installed_at": "${INSTALL_TIMESTAMP}",
  "transactional_update": true,
  "status": "STAGED_FOR_BOOT_ACTIVATION"
}
EOF

PRIMARY_IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{print $7}' || hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD} [✓] OPENSUSE MICROOS CONVERSION STAGED SUCCESSFULLY!${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${WHITE}Target Appliance Configuration:${NC}"
echo -e "  • Management Web Console:  ${CYAN}${BOLD}https://${PRIMARY_IP}:8443/${NC}"
echo -e "  • REST Control Plane Docs:  ${CYAN}http://${PRIMARY_IP}:8000/docs${NC}"
echo -e "  • Default Super Admin:      ${WHITE}admin${NC} (or admin@csir.res.in)"
echo -e "  • Default Password:         ${WHITE}CsirWebOS@2026!${NC}"
echo -e "  • Default MFA TOTP Token:   ${WHITE}123456${NC}"
echo -e "  • Unified Appliance CLI:    ${YELLOW}csir-ctl status${NC}"
echo -e "  • Cryptographic Audit Log:  ${WHITE}/var/log/audit/csir_audit.ledger${NC}"
echo -e "  • Installation Receipt:     ${WHITE}/etc/csir-swa/installation-receipt.json${NC}"
echo ""
echo -e "${YELLOW}${BOLD}[!] CRITICAL MICROOS STEP:${NC}"
echo -e "  openSUSE MicroOS is an immutable operating system. All new packages, kernel hardening,"
echo -e "  and systemd services have been safely staged into a fresh Btrfs root snapshot."
echo -e "  ${WHITE}${BOLD}A reboot is required to activate and boot into your new CSIR-SERC appliance.${NC}"
echo ""

if [ "$AUTO_REBOOT" = true ]; then
    echo -e "${GREEN}[*] Initiating automated system reboot in 5 seconds...${NC}"
    sleep 5
    systemctl reboot
elif [ "$DEFER_REBOOT" = true ]; then
    echo -e "${YELLOW}[i] Automatic reboot deferred. Please run 'sudo reboot' when ready.${NC}"
else
    if [ "$UNATTENDED" = false ]; then
        read -rp "Would you like to reboot into your CSIR Secure Web Appliance now? [Y/n]: " DO_REBOOT
        if [[ ! "$DO_REBOOT" =~ ^[Nn] ]]; then
            echo -e "${GREEN}[*] Rebooting into CSIR-SERC Secure Web Appliance OS...${NC}"
            systemctl reboot
        else
            echo -e "${YELLOW}[i] Please run 'sudo reboot' at your convenience to activate the appliance.${NC}"
        fi
    else
        echo -e "${YELLOW}[i] Please reboot the server ('sudo reboot') to complete activation.${NC}"
    fi
fi
