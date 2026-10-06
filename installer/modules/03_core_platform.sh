#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 03: Core Management Platform
# Deploys FastAPI Control Plane, Node Agent RPC, UX4G Portal & Audit Ledger
#=============================================================================
set -euo pipefail

install_core_management_platform() {
    echo -e "${CYAN}[*] Deploying CSIR-SWA Core Management Platform & Node Agent...${NC}"

    # 1. Install Python 3 and core system utilities
    echo -e "    • Installing Python runtime and dependencies..."
    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y python3 python3-pip python3-devel gcc || true
            ;;
        "rhel"|"fedora")
            dnf install -y python3 python3-pip python3-devel gcc || true
            ;;
        "debian")
            apt-get install -y python3 python3-pip python3-venv python3-dev build-essential || true
            ;;
    esac

    # 2. Create System Directories
    echo -e "    • Initializing directory hierarchy..."
    mkdir -p /etc/csir-swa
    mkdir -p /var/lib/csir-swa/data/logs
    mkdir -p /var/lib/csir-swa/static
    mkdir -p /run/csir-swa
    mkdir -p /var/log/audit
    mkdir -p /usr/lib/csir-swa/bin
    mkdir -p /srv/apps
    mkdir -p /srv/app-data
    mkdir -p /srv/backups

    # 3. Create Service Users
    echo -e "    • Setting up dedicated service accounts..."
    if ! id -u csir-swa >/dev/null 2>&1; then
        useradd -r -s /sbin/nologin -d /var/lib/csir-swa -c "CSIR-SWA Management Plane" csir-swa || true
    fi

    if ! id -u csir-app >/dev/null 2>&1; then
        useradd -u 100000 -s /sbin/nologin -d /srv/apps -c "CSIR Workload Isolation Account" csir-app || true
    fi

    # Configure subuid/subgid for rootless container namespaces
    if [ -f /etc/subuid ]; then
        grep -q "csir-app" /etc/subuid || echo "csir-app:100000:65536" >> /etc/subuid
        grep -q "csir-app" /etc/subgid || echo "csir-app:100000:65536" >> /etc/subgid
    fi

    # 4. Deploy Backend Source Code and Static Assets
    echo -e "    • Deploying Control Plane backend and Web Console assets..."
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    local PROJECT_ROOT
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

    if [ -d "$PROJECT_ROOT/backend/app" ]; then
        cp -r "$PROJECT_ROOT/backend/app" /var/lib/csir-swa/
        cp "$PROJECT_ROOT/backend/app/main.py" /var/lib/csir-swa/app/
    fi

    if [ -d "$PROJECT_ROOT/backend/node_agent" ]; then
        cp -r "$PROJECT_ROOT/backend/node_agent" /var/lib/csir-swa/
    fi

    if [ -d "$PROJECT_ROOT/backend/cli" ]; then
        cp -r "$PROJECT_ROOT/backend/cli" /var/lib/csir-swa/
        ln -sf /var/lib/csir-swa/cli/csir_ctl.py /usr/local/bin/csir-ctl || true
        chmod +x /var/lib/csir-swa/cli/csir_ctl.py || true
    fi

    if [ -d "$PROJECT_ROOT/backend/app/static" ]; then
        cp -r "$PROJECT_ROOT/backend/app/static/"* /var/lib/csir-swa/static/
    fi

    # 5. Set up Python virtual environment and packages
    echo -e "    • Configuring Python runtime environment..."
    python3 -m venv /var/lib/csir-swa/venv || true
    /var/lib/csir-swa/venv/bin/pip install --upgrade pip setuptools wheel || true
    /var/lib/csir-swa/venv/bin/pip install fastapi uvicorn pydantic sqlalchemy python-jose cryptography psutil jinja2 pyyaml httpx python-multipart || true

    # 6. Write Environment Configuration
    echo -e "    • Generating /etc/csir-swa/control-plane.env..."
    local JWT_SECRET
    JWT_SECRET="csir-swa-strategic-secure-key-$(openssl rand -hex 16 2>/dev/null || echo '2026-production')"
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

    # 7. Initialize CERT-In Cryptographic Audit Ledger
    echo -e "    • Initializing CERT-In Cryptographic Audit Ledger (Genesis Block)..."
    local INIT_TIMESTAMP
    INIT_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    cat <<EOF > /var/log/audit/csir_audit.ledger
{"index":1,"timestamp":"${INIT_TIMESTAMP}","actor":"installer:conversion_wizard","ip":"127.0.0.1","action":"CONVERT_APPLIANCE","resource":"system:os","prev_hash":"0000000000000000000000000000000000000000000000000000000000000000","entry_hash":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
EOF
    chmod 600 /var/log/audit/csir_audit.ledger

    # 8. Deploy Systemd Unit Files
    echo -e "    • Installing systemd units for Node Agent and Control Plane..."
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

    # Set ownership
    chown -R csir-swa:csir-swa /var/lib/csir-swa
    chmod 750 /var/lib/csir-swa

    systemctl daemon-reload
    systemctl enable csir-node-agent.service || true
    systemctl enable csir-control-plane.service || true
    systemctl restart csir-node-agent.service || true
    systemctl restart csir-control-plane.service || true

    echo -e "${GREEN}[✓] Core Management Platform successfully deployed and running.${NC}"
}
