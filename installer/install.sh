#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC SECURE WEB APPLIANCE OS (CSIR-SWA OS)
# Universal Online Remote Bootstrap Launcher
#
# Supported Distros:
#   • openSUSE MicroOS / Leap Micro / SUSE Linux Micro (Transactional Mode)
#   • openSUSE Leap 15.x / Tumbleweed
#   • Rocky Linux 8 / 9 / 10
#   • AlmaLinux 8 / 9 / 10
#   • Fedora Linux 39+
#
# One-Line Remote Usage:
#   Interactive:
#     curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash
#
#   Unattended Full Conversion with Automatic Reboot:
#     curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash -s -- --unattended --all --reboot
#
#   Specific Profile (e.g. Edge WAF):
#     curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash -s -- --profile edge-waf --reboot
#
#   Using Environment Variables:
#     export CSIR_PROFILE="full" CSIR_UNATTENDED="true" CSIR_REBOOT="true"
#     curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo -E bash
#=============================================================================
set -euo pipefail

# ANSI Color Codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat <<'EOF'
  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║                                                                              ║
  ║                   CSIR SECURE WEB APPLIANCE BOOTSTRAP                        ║
  ║             CSIR-SERC Immutable Web, Application and Security OS             ║
  ║                                                                              ║
  ║  Universal Online Bootstrap for Physical Servers, Cloud VMs & Appliances    ║
  ║                                                                              ║
  ╚══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# 1. Root Privileges Check
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo -e "${RED}[!] Error: Root privileges required. Please execute with sudo or as root:${NC}" >&2
    echo -e "    curl -sSL https://.../install.sh | ${WHITE}sudo bash${NC}" >&2
    exit 1
fi

# 2. Parse Environment Variables and CLI Flags
REPO_OWNER="ananthkrishnangv"
REPO_NAME="CSIR-SERC-Web-Appliance-OS"
BRANCH="${CSIR_BRANCH:-main}"
TARBALL_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/${BRANCH}.tar.gz"
GIT_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}.git"

FORWARDED_ARGS=()
HAS_UNATTENDED=false

# Support environment variables
if [ "${CSIR_UNATTENDED:-false}" = "true" ] || [ "${CSIR_UNATTENDED:-false}" = "1" ]; then
    FORWARDED_ARGS+=("--unattended")
    HAS_UNATTENDED=true
fi

if [ -n "${CSIR_PROFILE:-}" ]; then
    FORWARDED_ARGS+=("--profile" "${CSIR_PROFILE}")
fi

if [ "${CSIR_REBOOT:-false}" = "true" ] || [ "${CSIR_REBOOT:-false}" = "1" ]; then
    FORWARDED_ARGS+=("--reboot")
fi

if [ "${CSIR_ALL:-false}" = "true" ] || [ "${CSIR_ALL:-false}" = "1" ]; then
    FORWARDED_ARGS+=("--all")
fi

# Forward CLI arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --unattended|-y)
            HAS_UNATTENDED=true
            FORWARDED_ARGS+=("$1")
            shift
            ;;
        *)
            FORWARDED_ARGS+=("$1")
            shift
            ;;
    esac
done

# 3. Handle Stdin Piping vs Interactive Terminal
# If piped from curl/wget and NOT unattended, reconnect stdin to /dev/tty so interactive menus work
if [ ! -t 0 ] && [ "$HAS_UNATTENDED" = false ]; then
    if [ -e /dev/tty ]; then
        exec < /dev/tty
    else
        echo -e "${YELLOW}[!] Warning: No interactive terminal (/dev/tty) detected while running via pipe.${NC}"
        echo -e "${YELLOW}[!] Defaulting to unattended mode (--unattended --all)...${NC}"
        FORWARDED_ARGS+=("--unattended" "--all")
        HAS_UNATTENDED=true
    fi
fi

# 4. OS & Environment Detection
echo -e "${CYAN}[*] Inspecting host environment...${NC}"
IS_MICROOS=false
DISTRO_NAME="Unknown Linux"

if [ -f /etc/os-release ]; then
    # shellcheck source=/dev/null
    . /etc/os-release
    DISTRO_NAME="${NAME:-Unknown Linux}"
    if [[ "${ID:-}" == *"microos"* ]] || [[ "${NAME:-}" == *"MicroOS"* ]] || [[ "${NAME:-}" == *"Leap Micro"* ]] || [[ "${NAME:-}" == *"SL Micro"* ]]; then
        IS_MICROOS=true
    fi
fi

echo -e "    • Detected OS: ${WHITE}${DISTRO_NAME}${NC}"
if [ "$IS_MICROOS" = true ]; then
    echo -e "    • Target Engine: ${GREEN}openSUSE MicroOS Transactional Appliance Engine${NC}"
else
    echo -e "    • Target Engine: ${GREEN}Universal Linux Appliance Engine${NC}"
fi

# 5. Acquire Repository Payload (No git dependency required)
INSTALL_TMP=$(mktemp -d /tmp/csir-bootstrap-XXXXXX)
cleanup() {
    echo -e "\n${BLUE}[*] Cleaning temporary deployment artifacts...${NC}"
    rm -rf "$INSTALL_TMP" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo -e "${CYAN}[*] Downloading CSIR-SERC Web Appliance OS repository payload...${NC}"

DOWNLOAD_SUCCESS=false

# Method A: Download lightweight tarball via curl or wget (works on 100% of minimal distros)
if command -v curl >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
    echo -e "    • Fetching archive via curl: ${WHITE}${TARBALL_URL}${NC}"
    if curl -sSL --fail "$TARBALL_URL" | tar -xz -C "$INSTALL_TMP"; then
        DOWNLOAD_SUCCESS=true
    fi
elif command -v wget >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
    echo -e "    • Fetching archive via wget: ${WHITE}${TARBALL_URL}${NC}"
    if wget -qO- "$TARBALL_URL" | tar -xz -C "$INSTALL_TMP"; then
        DOWNLOAD_SUCCESS=true
    fi
fi

# Method B: Fallback to git clone if tarball download failed
if [ "$DOWNLOAD_SUCCESS" = false ]; then
    if command -v git >/dev/null 2>&1; then
        echo -e "    • Fetching via git clone: ${WHITE}${GIT_URL}${NC}"
        if git clone --depth 1 -b "$BRANCH" "$GIT_URL" "$INSTALL_TMP/${REPO_NAME}-${BRANCH}"; then
            DOWNLOAD_SUCCESS=true
        fi
    fi
fi

if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo -e "${RED}[!] Error: Failed to download CSIR-SERC appliance payload.${NC}" >&2
    echo -e "    Please verify internet connectivity and DNS resolution." >&2
    exit 1
fi

REPO_DIR="$INSTALL_TMP/${REPO_NAME}-${BRANCH}"
if [ ! -d "$REPO_DIR" ]; then
    # Try locating any extracted folder
    REPO_DIR=$(find "$INSTALL_TMP" -maxdepth 1 -type d -name "*${REPO_NAME}*" | head -n 1)
fi

if [ ! -d "$REPO_DIR/installer" ]; then
    echo -e "${RED}[!] Error: Corrupted payload structure. installer/ directory not found.${NC}" >&2
    exit 1
fi

echo -e "${GREEN}[✓] Appliance payload successfully extracted to temporary staging.${NC}"

# 6. Execute Conversion
cd "$REPO_DIR/installer"
chmod +x setup-appliance.sh convert-microos.sh modules/*.sh 2>/dev/null || true

echo ""
if [ "$IS_MICROOS" = true ]; then
    echo -e "${CYAN}${BOLD}[*] Launching openSUSE MicroOS Transactional Appliance Converter...${NC}"
    ./convert-microos.sh "${FORWARDED_ARGS[@]}"
else
    echo -e "${CYAN}${BOLD}[*] Launching Universal Appliance Converter...${NC}"
    ./setup-appliance.sh "${FORWARDED_ARGS[@]}"
fi
