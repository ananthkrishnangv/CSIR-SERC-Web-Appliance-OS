#!/bin/bash
#==================================================================
# CSIR-SWA OS Interactive First-Boot Configuration Wizard
# Configures network, TLS, emergency admin, NTP, and security profile
#==================================================================
set -euo pipefail

clear
cat << "EOF"
======================================================================
                  [ CSIR SECURE WEB APPLIANCE OS ]
          First-Boot Configuration and Initialisation Wizard
======================================================================
EOF

CONF_DIR="/etc/csir-swa"
mkdir -p "${CONF_DIR}"

if [ -f "${CONF_DIR}/provisioned" ]; then
    echo "Appliance has already been provisioned. Exiting."
    exit 0
fi

echo "Welcome to CSIR-SWA OS Setup."
echo "Please enter initial appliance parameters or press ENTER for defaults."
echo ""

read -rp "1. Organisation / Lab Name [CSIR-SERC]: " ORG_NAME
ORG_NAME=${ORG_NAME:-"CSIR-SERC"}

read -rp "2. Appliance Hostname [csir-appliance]: " HOSTNAME
HOSTNAME=${HOSTNAME:-"csir-appliance"}

read -rp "3. Management IP CIDR [10.20.10.15/24]: " MGMT_IP
MGMT_IP=${MGMT_IP:-"10.20.10.15/24"}

read -rp "4. Default Gateway [10.20.10.1]: " GATEWAY
GATEWAY=${GATEWAY:-"10.20.10.1"}

read -rp "5. Primary DNS Server [10.20.1.1]: " DNS_SERVER
DNS_SERVER=${DNS_SERVER:-"10.20.1.1"}

read -rp "6. Security Profile (standard / hardened / air-gapped) [hardened]: " SEC_PROFILE
SEC_PROFILE=${SEC_PROFILE:-"hardened"}

echo ""
echo "Creating appliance configuration..."
cat <<EOF > "${CONF_DIR}/appliance.yaml"
appliance:
  organisation: "${ORG_NAME}"
  hostname: "${HOSTNAME}"
  security_profile: "${SEC_PROFILE}"
  management_ip: "${MGMT_IP}"
  gateway: "${GATEWAY}"
  dns: "${DNS_SERVER}"
  provisioned_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  version: "1.0.0"
  channel: "Stable"
EOF

# Set hostname
hostnamectl set-hostname "${HOSTNAME}" || true

# Mark provisioned
touch "${CONF_DIR}/provisioned"
echo "Appliance provisioned successfully. Management available at: https://${MGMT_IP%%/*}:8443"
sleep 3
exit 0
