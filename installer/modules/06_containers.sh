#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 06: Container & Workload Engine
# Deploys Podman 6.x Quadlet Engine, rootless namespaces & certified templates
#=============================================================================
set -euo pipefail

install_container_engine() {
    echo -e "${CYAN}[*] Installing Container & Workload Platform (Podman Quadlets)...${NC}"

    # 1. Install Podman, crun, and Netavark
    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y podman crun netavark aardvark-dns catatonit || true
            ;;
        "rhel"|"fedora")
            dnf install -y podman crun netavark aardvark-dns catatonit || true
            ;;
        "debian")
            apt-get install -y podman crun netavark aardvark-dns catatonit || true
            ;;
    esac

    # 2. Configure System-wide Quadlet directories
    mkdir -p /etc/containers/systemd
    mkdir -p /etc/containers/registries.conf.d

    # 3. Configure Secure Container Registry Policy
    cat <<EOF > /etc/containers/registries.conf.d/00-csir-registries.conf
unqualified-search-registries = ["registry.csir.res.in", "docker.io", "quay.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry]]
prefix = "registry.csir.res.in"
location = "registry.csir.res.in"
EOF

    # 4. Deploy Certified Systemd Quadlets from Templates
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    local PROJECT_ROOT
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

    echo -e "    • Deploying certified application Quadlets..."
    if [ -d "$PROJECT_ROOT/templates" ]; then
        cp -r "$PROJECT_ROOT/templates/"* /srv/apps/ 2>/dev/null || true
        find "$PROJECT_ROOT/templates" -name "*.container" -o -name "*.network" | while read -r qfile; do
            cp "$qfile" /etc/containers/systemd/
            echo -e "      - Installed Quadlet: $(basename "$qfile")"
        done
    fi

    # Fallback default Quadlet if templates not present
    if [ ! -f /etc/containers/systemd/csir-portal.container ]; then
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
        cat <<EOF > /srv/apps/portal-data/index.html
<!DOCTYPE html>
<html>
<head><title>CSIR-SERC Research Portal</title></head>
<body style="font-family:sans-serif; text-align:center; padding:50px; background:#0b1d33; color:#fff;">
<h1>CSIR-SERC Research Portal Workload</h1>
<p>Containerised Quadlet application running securely on CSIR Secure Web Appliance OS.</p>
</body>
</html>
EOF
    fi

    # 5. Reload systemd to generate services from Quadlets
    echo -e "    • Generating systemd services from Quadlets..."
    systemctl daemon-reload
    systemctl enable podman-auto-update.timer || true

    echo -e "${GREEN}[✓] Podman Quadlet container workload engine configured.${NC}"
}
