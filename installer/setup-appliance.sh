#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC SECURE WEB APPLIANCE OS (CSIR-SWA OS)
# Universal Appliance Conversion & Installation Wizard
# Baseline: openSUSE MicroOS, openSUSE Leap, Rocky Linux, AlmaLinux, Fedora
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

# Ensure root privileges
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo -e "${RED}[!] Error: This installation wizard must be run with root privileges (sudo).${NC}" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="${SCRIPT_DIR}/modules"

# Source all modular sub-engines
if [ -d "$MODULES_DIR" ]; then
    for mod in "$MODULES_DIR"/*.sh; do
        if [ -f "$mod" ]; then
            # shellcheck source=/dev/null
            . "$mod"
        fi
    done
else
    echo -e "${RED}[!] Error: Modules directory not found at $MODULES_DIR${NC}" >&2
    exit 1
fi

print_banner() {
    clear 2>/dev/null || true
    echo -e "${CYAN}${BOLD}"
    cat <<'EOF'
  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║                                                                              ║
  ║                   CSIR SECURE WEB APPLIANCE CONVERTER                        ║
  ║             CSIR-SERC Immutable Web, Application and Security OS             ║
  ║                                                                              ║
  ║  Converts openSUSE MicroOS / Leap, Rocky Linux, AlmaLinux & Fedora into      ║
  ║  a hardened, tamper-evident institutional web appliance platform.            ║
  ║                                                                              ║
  ╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

usage() {
    cat <<EOF
Usage: sudo ./setup-appliance.sh [OPTIONS]

Options:
  --help, -h             Show this help message and exit
  --unattended, -y       Run in non-interactive / unattended automated mode
  --all, -a              Install all 12 platform subsystems (Monolithic Full Stack)
  --profile <NAME>       Select predefined deployment profile:
                           full       - All services (Web, WAF, Podman, DB, DR, AI, Branding)
                           edge-waf   - Reverse Proxy, Coraza WAF, Firewall, Hardening, Branding
                           app-host   - Containers, DB, Proxy, Hardening, Branding
                           minimal    - Core Management, Firewall, Hardening only
  --services <LIST>      Comma-separated list of services to install (e.g. 1,2,3,4,5,11,12)

Examples:
  sudo ./setup-appliance.sh                          # Interactive Wizard
  sudo ./setup-appliance.sh --unattended --all       # Zero-touch full installation
  sudo ./setup-appliance.sh --profile edge-waf       # Deploy Edge WAF profile
EOF
    exit 0
}

# Default Configuration Flags
UNATTENDED=false
INSTALL_ALL=false
SELECTED_PROFILE=""
CUSTOM_SERVICES=""

# Parse Command Line Arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h)
            usage
            ;;
        --unattended|-y)
            UNATTENDED=true
            shift
            ;;
        --all|-a)
            INSTALL_ALL=true
            shift
            ;;
        --profile)
            SELECTED_PROFILE="$2"
            shift 2
            ;;
        --services)
            CUSTOM_SERVICES="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}[!] Unknown argument: $1${NC}"
            usage
            ;;
    esac
done

# Initialize Service Selections (0 = No, 1 = Yes)
INSTALL_CORE=1
INSTALL_PROXY=1
INSTALL_WAF=1
INSTALL_FIREWALL=1
INSTALL_CONTAINERS=1
INSTALL_DATABASE=1
INSTALL_VIRTUALIZATION=1
INSTALL_BACKUPS=1
INSTALL_OBSERVABILITY=1
INSTALL_AI_SECURITY=1
INSTALL_HARDENING=1
INSTALL_BRANDING=1

apply_profile() {
    local prof="$1"
    case "$prof" in
        "full")
            INSTALL_CORE=1; INSTALL_PROXY=1; INSTALL_WAF=1; INSTALL_FIREWALL=1
            INSTALL_CONTAINERS=1; INSTALL_DATABASE=1; INSTALL_VIRTUALIZATION=1
            INSTALL_BACKUPS=1; INSTALL_OBSERVABILITY=1; INSTALL_AI_SECURITY=1
            INSTALL_HARDENING=1; INSTALL_BRANDING=1
            ;;
        "edge-waf")
            INSTALL_CORE=1; INSTALL_PROXY=1; INSTALL_WAF=1; INSTALL_FIREWALL=1
            INSTALL_CONTAINERS=0; INSTALL_DATABASE=0; INSTALL_VIRTUALIZATION=0
            INSTALL_BACKUPS=1; INSTALL_OBSERVABILITY=1; INSTALL_AI_SECURITY=1
            INSTALL_HARDENING=1; INSTALL_BRANDING=1
            ;;
        "app-host")
            INSTALL_CORE=1; INSTALL_PROXY=1; INSTALL_WAF=0; INSTALL_FIREWALL=1
            INSTALL_CONTAINERS=1; INSTALL_DATABASE=1; INSTALL_VIRTUALIZATION=0
            INSTALL_BACKUPS=1; INSTALL_OBSERVABILITY=1; INSTALL_AI_SECURITY=0
            INSTALL_HARDENING=1; INSTALL_BRANDING=1
            ;;
        "minimal")
            INSTALL_CORE=1; INSTALL_PROXY=0; INSTALL_WAF=0; INSTALL_FIREWALL=1
            INSTALL_CONTAINERS=0; INSTALL_DATABASE=0; INSTALL_VIRTUALIZATION=0
            INSTALL_BACKUPS=0; INSTALL_OBSERVABILITY=0; INSTALL_AI_SECURITY=0
            INSTALL_HARDENING=1; INSTALL_BRANDING=1
            ;;
        *)
            echo -e "${RED}[!] Invalid profile: $prof. Defaulting to full.${NC}"
            apply_profile "full"
            ;;
    esac
}

# Run Step 1: Detect Operating System
print_banner
detect_operating_system

# Route openSUSE MicroOS directly to the specialized transactional converter
if [ "${IS_TRANSACTIONAL:-false}" = true ] && [ -f "${SCRIPT_DIR}/convert-microos.sh" ]; then
    echo ""
    echo -e "${YELLOW}[i] openSUSE MicroOS detected (Transactional Update & Immutable Root).${NC}"
    echo -e "${CYAN}[*] Engaging dedicated openSUSE MicroOS Transactional Appliance Converter...${NC}"
    echo ""
    exec "${SCRIPT_DIR}/convert-microos.sh" "$@"
fi

# Wizard Menu Selection
if [ "$UNATTENDED" = false ] && [ "$INSTALL_ALL" = false ] && [ -z "$SELECTED_PROFILE" ] && [ -z "$CUSTOM_SERVICES" ]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Select Appliance Deployment Profile:${NC}"
    echo -e "  ${WHITE}1)${NC} ${GREEN}${BOLD}[Recommended] Complete Full-Stack Web Appliance${NC} (All 12 Modules)"
    echo -e "     - Core Portal, HAProxy, Coraza WAF, nftables, Podman, PostgreSQL, Snapper/Restic, AI Center, Boot Branding"
    echo -e "  ${WHITE}2)${NC} ${CYAN}Edge Security & WAF Appliance${NC}"
    echo -e "     - Reverse Proxy, Coraza WAF, nftables, Suricata, Hardening, Visual Branding"
    echo -e "  ${WHITE}3)${NC} ${BLUE}Application & Workload Host${NC}"
    echo -e "     - Core Portal, Podman Quadlets, PostgreSQL, Backups, Hardening"
    echo -e "  ${WHITE}4)${NC} ${MAGENTA}Minimal Core Appliance${NC}"
    echo -e "     - Core Management, Node Agent, nftables, Hardening only"
    echo -e "  ${WHITE}5)${NC} ${WHITE}Custom Component Selection (Configure individually)${NC}"
    echo ""
    read -rp "Enter choice [1-5, default: 1]: " PROFILE_CHOICE
    PROFILE_CHOICE="${PROFILE_CHOICE:-1}"

    case "$PROFILE_CHOICE" in
        1) apply_profile "full" ;;
        2) apply_profile "edge-waf" ;;
        3) apply_profile "app-host" ;;
        4) apply_profile "minimal" ;;
        5)
            echo ""
            echo -e "${YELLOW}${BOLD}Custom Subsystem Selection (Enter y/n for each):${NC}"
            read -rp "  [1] Core Management (FastAPI, UX4G Portal, Node Agent, Audit Ledger)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_CORE=0 || INSTALL_CORE=1
            read -rp "  [2] Web Delivery & Reverse Proxy (HAProxy, TLS 1.3)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_PROXY=0 || INSTALL_PROXY=1
            read -rp "  [3] Web Application Firewall (Coraza WAF + OWASP CRS v4)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_WAF=0 || INSTALL_WAF=1
            read -rp "  [4] Host Firewall & Network Defense (nftables default-deny, Suricata)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_FIREWALL=0 || INSTALL_FIREWALL=1
            read -rp "  [5] Container & Workload Engine (Podman 6.x Quadlets, templates)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_CONTAINERS=0 || INSTALL_CONTAINERS=1
            read -rp "  [6] Database Subsystem (PostgreSQL 17, PgBouncer)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_DATABASE=0 || INSTALL_DATABASE=1
            read -rp "  [7] Virtualization Subsystem (KVM, QEMU, libvirt)? [y/N]: " ans; [[ "$ans" =~ ^[Yy] ]] && INSTALL_VIRTUALIZATION=1 || INSTALL_VIRTUALIZATION=0
            read -rp "  [8] Data Protection & Backups (Snapper snapshots, Restic, Borg)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_BACKUPS=0 || INSTALL_BACKUPS=1
            read -rp "  [9] Observability & Telemetry (Prometheus, Grafana)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_OBSERVABILITY=0 || INSTALL_OBSERVABILITY=1
            read -rp " [10] Local AI Security Center (Threat Correlation, ChatOps)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_AI_SECURITY=0 || INSTALL_AI_SECURITY=1
            read -rp " [11] System Hardening & Compliance (CERT-In, sysctl, SSH, banners)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_HARDENING=0 || INSTALL_HARDENING=1
            read -rp " [12] Bootloader & Visual Branding (CSIR-SERC Boot Splash & GRUB)? [Y/n]: " ans; [[ "$ans" =~ ^[Nn] ]] && INSTALL_BRANDING=0 || INSTALL_BRANDING=1
            ;;
        *) apply_profile "full" ;;
    esac
elif [ -n "$SELECTED_PROFILE" ]; then
    apply_profile "$SELECTED_PROFILE"
elif [ "$INSTALL_ALL" = true ]; then
    apply_profile "full"
elif [ -n "$CUSTOM_SERVICES" ]; then
    INSTALL_CORE=0; INSTALL_PROXY=0; INSTALL_WAF=0; INSTALL_FIREWALL=0
    INSTALL_CONTAINERS=0; INSTALL_DATABASE=0; INSTALL_VIRTUALIZATION=0
    INSTALL_BACKUPS=0; INSTALL_OBSERVABILITY=0; INSTALL_AI_SECURITY=0
    INSTALL_HARDENING=0; INSTALL_BRANDING=0
    IFS=',' read -ra ADDR <<< "$CUSTOM_SERVICES"
    for num in "${ADDR[@]}"; do
        case "$num" in
            1) INSTALL_CORE=1 ;;
            2) INSTALL_PROXY=1 ;;
            3) INSTALL_WAF=1 ;;
            4) INSTALL_FIREWALL=1 ;;
            5) INSTALL_CONTAINERS=1 ;;
            6) INSTALL_DATABASE=1 ;;
            7) INSTALL_VIRTUALIZATION=1 ;;
            8) INSTALL_BACKUPS=1 ;;
            9) INSTALL_OBSERVABILITY=1 ;;
            10) INSTALL_AI_SECURITY=1 ;;
            11) INSTALL_HARDENING=1 ;;
            12) INSTALL_BRANDING=1 ;;
        esac
    done
fi

# Summary Confirmation
echo ""
echo -e "${CYAN}${BOLD}=== Component Deployment Matrix ===${NC}"
[ "$INSTALL_CORE" -eq 1 ] && echo -e "  ${GREEN}[✓] Core Management Platform (FastAPI, UX4G Portal, Node Agent, Audit Ledger)${NC}" || echo -e "  ${RED}[ ] Core Management Platform${NC}"
[ "$INSTALL_PROXY" -eq 1 ] && echo -e "  ${GREEN}[✓] Web Delivery & Reverse Proxy (HAProxy, TLS 1.3 Termination)${NC}" || echo -e "  ${RED}[ ] Web Delivery & Reverse Proxy${NC}"
[ "$INSTALL_WAF" -eq 1 ] && echo -e "  ${GREEN}[✓] Web Application Firewall (Coraza WAF + OWASP Core Rule Set v4)${NC}" || echo -e "  ${RED}[ ] Web Application Firewall${NC}"
[ "$INSTALL_FIREWALL" -eq 1 ] && echo -e "  ${GREEN}[✓] Host Firewall & Network Defense (nftables default-deny, Suricata 7.0)${NC}" || echo -e "  ${RED}[ ] Host Firewall & Network Defense${NC}"
[ "$INSTALL_CONTAINERS" -eq 1 ] && echo -e "  ${GREEN}[✓] Container & Workload Engine (Rootless Podman 6.x Quadlets, Templates)${NC}" || echo -e "  ${RED}[ ] Container & Workload Engine${NC}"
[ "$INSTALL_DATABASE" -eq 1 ] && echo -e "  ${GREEN}[✓] Database Subsystem (PostgreSQL 17, PgBouncer Pooler)${NC}" || echo -e "  ${RED}[ ] Database Subsystem${NC}"
[ "$INSTALL_VIRTUALIZATION" -eq 1 ] && echo -e "  ${GREEN}[✓] Virtualization Subsystem (KVM, QEMU, libvirt Hypervisor)${NC}" || echo -e "  ${RED}[ ] Virtualization Subsystem${NC}"
[ "$INSTALL_BACKUPS" -eq 1 ] && echo -e "  ${GREEN}[✓] Data Protection & Backups (Btrfs Snapper, Restic, Borg, DR Drill Engine)${NC}" || echo -e "  ${RED}[ ] Data Protection & Backups${NC}"
[ "$INSTALL_OBSERVABILITY" -eq 1 ] && echo -e "  ${GREEN}[✓] Observability & Telemetry (Prometheus Metrics, Grafana Visual Dashboards)${NC}" || echo -e "  ${RED}[ ] Observability & Telemetry${NC}"
[ "$INSTALL_AI_SECURITY" -eq 1 ] && echo -e "  ${GREEN}[✓] Local AI Security Center (Threat Correlation, WAF Analyzer, ChatOps)${NC}" || echo -e "  ${RED}[ ] Local AI Security Center${NC}"
[ "$INSTALL_HARDENING" -eq 1 ] && echo -e "  ${GREEN}[✓] System Hardening & Compliance (Kernel sysctl, limits, SSH, Banners)${NC}" || echo -e "  ${RED}[ ] System Hardening & Compliance${NC}"
[ "$INSTALL_BRANDING" -eq 1 ] && echo -e "  ${GREEN}[✓] Bootloader & Visual Branding (CSIR-SERC Boot Splash & GRUB Theme)${NC}" || echo -e "  ${RED}[ ] Bootloader & Visual Branding${NC}"
echo ""

if [ "$UNATTENDED" = false ]; then
    read -rp "Proceed with appliance conversion? [Y/n]: " CONFIRM
    if [[ "$CONFIRM" =~ ^[Nn] ]]; then
        echo -e "${YELLOW}[i] Installation aborted by user.${NC}"
        exit 0
    fi
fi

# Execution Pipeline
echo ""
echo -e "${CYAN}${BOLD}=== Commencing CSIR-SERC Appliance Conversion ===${NC}"

# 1. Clean up legacy conflicts
cleanup_conflicting_services

# 2. Configure Repositories
configure_distribution_repositories

# 3. Execute Selected Modules
[ "$INSTALL_CORE" -eq 1 ] && install_core_management_platform
[ "$INSTALL_PROXY" -eq 1 ] && install_web_delivery_and_waf
[ "$INSTALL_FIREWALL" -eq 1 ] && install_firewall_and_network_defense
[ "$INSTALL_CONTAINERS" -eq 1 ] && install_container_engine
[ "$INSTALL_DATABASE" -eq 1 ] && install_database_platform
[ "$INSTALL_VIRTUALIZATION" -eq 1 ] && install_virtualization_subsystem
[ "$INSTALL_BACKUPS" -eq 1 ] && install_backup_and_disaster_recovery
[ "$INSTALL_OBSERVABILITY" -eq 1 ] && install_observability_and_monitoring
[ "$INSTALL_AI_SECURITY" -eq 1 ] && install_local_ai_security_center
[ "$INSTALL_HARDENING" -eq 1 ] && apply_system_hardening_and_compliance
[ "$INSTALL_BRANDING" -eq 1 ] && apply_bootloader_branding

# 4. Generate Installation Receipt
INSTALL_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat <<EOF > /etc/csir-swa/installation-receipt.json
{
  "product": "CSIR Secure Web Appliance OS",
  "version": "1.0.0",
  "deployment_type": "SCRIPT_BASED_CONVERSION",
  "base_distribution": "${DISTRO_NAME} (${DISTRO_ID} ${DISTRO_VERSION})",
  "installed_at": "${INSTALL_TIMESTAMP}",
  "modules_installed": {
    "core_management": $([ "$INSTALL_CORE" -eq 1 ] && echo true || echo false),
    "web_proxy": $([ "$INSTALL_PROXY" -eq 1 ] && echo true || echo false),
    "waf_coraza": $([ "$INSTALL_WAF" -eq 1 ] && echo true || echo false),
    "host_firewall": $([ "$INSTALL_FIREWALL" -eq 1 ] && echo true || echo false),
    "container_engine": $([ "$INSTALL_CONTAINERS" -eq 1 ] && echo true || echo false),
    "database": $([ "$INSTALL_DATABASE" -eq 1 ] && echo true || echo false),
    "virtualization": $([ "$INSTALL_VIRTUALIZATION" -eq 1 ] && echo true || echo false),
    "backups_dr": $([ "$INSTALL_BACKUPS" -eq 1 ] && echo true || echo false),
    "observability": $([ "$INSTALL_OBSERVABILITY" -eq 1 ] && echo true || echo false),
    "local_ai": $([ "$INSTALL_AI_SECURITY" -eq 1 ] && echo true || echo false),
    "hardening": $([ "$INSTALL_HARDENING" -eq 1 ] && echo true || echo false),
    "boot_branding": $([ "$INSTALL_BRANDING" -eq 1 ] && echo true || echo false)
  },
  "status": "OPERATIONAL"
}
EOF

# Determine Local Host IP
PRIMARY_IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{print $7}' || hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD} [✓] CSIR-SERC SECURE WEB APPLIANCE OS CONVERSION COMPLETED!${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${WHITE}Access Credentials & Management Endpoints:${NC}"
echo -e "  • Management Web Console:  ${CYAN}${BOLD}https://${PRIMARY_IP}:8443/${NC} *(or https://localhost:8443/)*"
echo -e "  • REST Control Plane Docs:  ${CYAN}http://${PRIMARY_IP}:8000/docs${NC}"
echo -e "  • Default Super Admin:      ${WHITE}admin${NC} (or admin@csir.res.in)"
echo -e "  • Default Password:         ${WHITE}CsirWebOS@2026!${NC}"
echo -e "  • Default MFA TOTP Token:   ${WHITE}123456${NC}"
echo -e "  • Unified Appliance CLI:    ${YELLOW}csir-ctl status${NC}"
echo -e "  • Cryptographic Audit Log:  ${WHITE}/var/log/audit/csir_audit.ledger${NC}"
echo -e "  • Installation Receipt:     ${WHITE}/etc/csir-swa/installation-receipt.json${NC}"
echo ""
echo -e "${YELLOW}[!] Note: If you installed Boot Branding, your next reboot will display the official CSIR-SERC Boot Splash.${NC}"
echo -e "${GREEN}${BOLD}System is now operating as a CSIR-SERC Secure Web Appliance.${NC}"
exit 0
