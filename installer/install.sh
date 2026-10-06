#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Quick One-Line Remote Bootstrap
# Usage: curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash
#=============================================================================
set -euo pipefail

REPO_URL="https://github.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS.git"
INSTALL_TMP="/tmp/csir-webos-installer-$(date +%s)"

echo "=== CSIR-SERC Secure Web Appliance OS Bootstrap Launcher ==="

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo "[!] Error: Root privileges required. Re-run with sudo." >&2
    exit 1
fi

# Ensure git or curl/tar are installed
if ! command -v git >/dev/null 2>&1; then
    echo "[*] Installing git for repository deployment..."
    if command -v zypper >/dev/null 2>&1; then
        zypper install -y git-core || true
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y git-core || true
    elif command -v apt-get >/dev/null 2>&1; then
        apt-get update -y && apt-get install -y git || true
    fi
fi

mkdir -p "$INSTALL_TMP"
echo "[*] Cloning CSIR-SERC Web Appliance repository..."
git clone --depth 1 "$REPO_URL" "$INSTALL_TMP/repo"

cd "$INSTALL_TMP/repo/installer"
chmod +x setup-appliance.sh modules/*.sh

echo "[*] Launching Universal Interactive Appliance Wizard..."
./setup-appliance.sh "$@"
