#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 01: Conflict Cleanup & Migration
# Safely disables and removes legacy/conflicting software before conversion
#=============================================================================
set -euo pipefail

cleanup_conflicting_services() {
    echo -e "${CYAN}[*] Inspecting running environment for conflicting services and ports...${NC}"
    
    local BACKUP_DIR="/var/backups/csir-preinstall-$(date +%Y%m%d%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # 1. Check and resolve Port 80 and 443 conflicts (Apache/Httpd/Old Webservers)
    echo -e "    • Auditing Web Delivery ports (80, 443)..."
    for s in httpd apache2 lighttpd caddy; do
        if systemctl is-active --quiet "$s" 2>/dev/null; then
            echo -e "${YELLOW}[!] Conflicting active webserver found: $s (occupying port 80/443). Stopping and disabling...${NC}"
            systemctl stop "$s" || true
            systemctl disable "$s" || true
            systemctl mask "$s" || true
            echo -e "${GREEN}[✓] Disabled conflicting webserver: $s${NC}"
        fi
    done

    # 2. Check and resolve Firewall conflicts (firewalld / ufw vs nftables)
    echo -e "    • Auditing Host Firewall services..."
    if systemctl is-active --quiet firewalld 2>/dev/null; then
        echo -e "${YELLOW}[!] firewalld is currently active. Backing up and switching to native nftables default-deny engine...${NC}"
        if [ -d /etc/firewalld ]; then
            cp -r /etc/firewalld "$BACKUP_DIR/firewalld.bak" 2>/dev/null || true
        fi
        systemctl stop firewalld || true
        systemctl disable firewalld || true
        systemctl mask firewalld || true
        echo -e "${GREEN}[✓] firewalld stopped and masked. nftables will manage host security.${NC}"
    fi

    if command -v ufw >/dev/null 2>&1; then
        if ufw status | grep -q "Status: active"; then
            echo -e "${YELLOW}[!] ufw active. Disabling in favor of nftables...${NC}"
            ufw disable || true
            systemctl disable ufw || true
        fi
    fi

    # 3. Clean stale CSIR Appliance Daemons and Sockets
    echo -e "    • Auditing existing CSIR appliance daemons and sockets..."
    for csir_svc in csir-control-plane csir-node-agent csir-health-gate; do
        if systemctl is-active --quiet "$csir_svc" 2>/dev/null; then
            echo -e "${BLUE}[i] Stopping existing instance of $csir_svc for clean upgrade...${NC}"
            systemctl stop "$csir_svc" || true
        fi
    done

    if [ -S "/run/csir-swa/agent.sock" ]; then
        rm -f "/run/csir-swa/agent.sock"
    fi

    # 4. Backup existing critical configs before modification
    for cfg in /etc/nftables.conf /etc/nftables/csir-firewall.nft /etc/haproxy/haproxy.cfg /etc/coraza/coraza.conf; do
        if [ -f "$cfg" ]; then
            cp "$cfg" "$BACKUP_DIR/" 2>/dev/null || true
        fi
    done

    echo -e "${GREEN}[✓] Conflict cleanup completed. Pre-existing configs preserved in ${BACKUP_DIR}${NC}"
}
