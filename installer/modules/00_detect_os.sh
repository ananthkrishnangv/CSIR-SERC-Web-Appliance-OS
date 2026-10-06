#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 00: OS & Environment Detection
#=============================================================================
set -euo pipefail

detect_operating_system() {
    echo -e "${CYAN}[*] Detecting underlying operating system and hardware platform...${NC}"

    if [ ! -f /etc/os-release ]; then
        echo -e "${RED}[!] Error: /etc/os-release not found. Unsupported distribution.${NC}" >&2
        return 1
    fi

    # Source os-release
    # shellcheck source=/dev/null
    . /etc/os-release

    DISTRO_NAME="${NAME:-Unknown}"
    DISTRO_ID="${ID:-unknown}"
    DISTRO_VERSION="${VERSION_ID:-unknown}"
    DISTRO_LIKE="${ID_LIKE:-}"
    IS_TRANSACTIONAL=false
    PKG_MGR=""

    # Detect Architecture
    ARCH=$(uname -m)
    if [ "$ARCH" != "x86_64" ] && [ "$ARCH" != "aarch64" ]; then
        echo -e "${RED}[!] Warning: CPU architecture $ARCH is non-standard. x86_64 or aarch64 recommended.${NC}" >&2
    fi

    # Classify distribution family and package manager
    if [[ "$DISTRO_ID" == *"microos"* ]] || [[ "$DISTRO_NAME" == *"MicroOS"* ]]; then
        DISTRO_FAMILY="suse"
        DISTRO_TYPE="opensuse-microos"
        IS_TRANSACTIONAL=true
        PKG_MGR="transactional-update"
    elif [[ "$DISTRO_ID" == "opensuse-leap" ]] || [[ "$DISTRO_ID" == "opensuse-tumbleweed" ]] || [[ "$DISTRO_LIKE" == *"suse"* ]]; then
        DISTRO_FAMILY="suse"
        DISTRO_TYPE="opensuse"
        PKG_MGR="zypper"
    elif [[ "$DISTRO_ID" == "rocky" ]] || [[ "$DISTRO_ID" == "almalinux" ]] || [[ "$DISTRO_ID" == "rhel" ]] || [[ "$DISTRO_ID" == "centos" ]]; then
        DISTRO_FAMILY="rhel"
        DISTRO_TYPE="$DISTRO_ID"
        PKG_MGR="dnf"
    elif [[ "$DISTRO_ID" == "fedora" ]]; then
        DISTRO_FAMILY="fedora"
        DISTRO_TYPE="fedora"
        PKG_MGR="dnf"
    elif [[ "$DISTRO_ID" == "ubuntu" ]] || [[ "$DISTRO_ID" == "debian" ]]; then
        DISTRO_FAMILY="debian"
        DISTRO_TYPE="$DISTRO_ID"
        PKG_MGR="apt"
    else
        # Fallback detection using package manager presence
        if command -v transactional-update >/dev/null 2>&1; then
            DISTRO_FAMILY="suse"
            DISTRO_TYPE="microos"
            IS_TRANSACTIONAL=true
            PKG_MGR="transactional-update"
        elif command -v zypper >/dev/null 2>&1; then
            DISTRO_FAMILY="suse"
            DISTRO_TYPE="opensuse"
            PKG_MGR="zypper"
        elif command -v dnf >/dev/null 2>&1; then
            DISTRO_FAMILY="rhel"
            DISTRO_TYPE="rhel-compatible"
            PKG_MGR="dnf"
        elif command -v apt-get >/dev/null 2>&1; then
            DISTRO_FAMILY="debian"
            DISTRO_TYPE="debian-compatible"
            PKG_MGR="apt"
        else
            echo -e "${RED}[!] Error: Could not determine package manager on this system.${NC}" >&2
            return 1
        fi
    fi

    # Memory Check
    TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
    CPU_CORES=$(nproc)
    DISK_FREE_GB=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')

    echo -e "${GREEN}[✓] System Identified:${NC}"
    echo -e "    • OS Name:            ${WHITE}${DISTRO_NAME} (${DISTRO_ID} ${DISTRO_VERSION})${NC}"
    echo -e "    • Distribution Family: ${WHITE}${DISTRO_FAMILY} (Package Manager: ${PKG_MGR})${NC}"
    echo -e "    • Immutable/Snapshot:  ${WHITE}${IS_TRANSACTIONAL}${NC}"
    echo -e "    • Hardware Resources:  ${WHITE}${CPU_CORES} vCPUs, ${TOTAL_RAM_MB} MB RAM, ${DISK_FREE_GB} GB Free Disk${NC}"

    if [ "$TOTAL_RAM_MB" -lt 1800 ]; then
        echo -e "${YELLOW}[!] Warning: System has ${TOTAL_RAM_MB} MB RAM (< 2048 MB recommended). Performance may be constrained.${NC}"
    fi

    export DISTRO_NAME DISTRO_ID DISTRO_VERSION DISTRO_FAMILY DISTRO_TYPE IS_TRANSACTIONAL PKG_MGR ARCH TOTAL_RAM_MB CPU_CORES DISK_FREE_GB
}
