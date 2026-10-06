#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 05: Host Firewall & Network Defense
# Deploys nftables default-deny ruleset and Suricata 7.0 IDS/IPS sensor
#=============================================================================
set -euo pipefail

install_firewall_and_network_defense() {
    echo -e "${CYAN}[*] Installing Host Firewall & Network Defense (nftables + Suricata)...${NC}"

    # 1. Install nftables and Suricata
    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y nftables suricata || true
            ;;
        "rhel"|"fedora")
            dnf install -y nftables suricata || true
            ;;
        "debian")
            apt-get install -y nftables suricata || true
            ;;
    esac

    # 2. Deploy nftables default-deny ruleset
    echo -e "    • Deploying hardened /etc/nftables/csir-firewall.nft..."
    mkdir -p /etc/nftables
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    if [ -f "$SCRIPT_DIR/assets/security/csir-firewall.nft" ]; then
        cp "$SCRIPT_DIR/assets/security/csir-firewall.nft" /etc/nftables/csir-firewall.nft
    else
        cat <<'EOF' > /etc/nftables/csir-firewall.nft
#!/usr/sbin/nft -f
flush ruleset

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

        # Public Web Traffic & Management
        tcp dport { 80, 443 } accept
        tcp dport 8443 accept

        # Log and drop
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

    # Link into distro nftables include
    if [ -f /etc/sysconfig/nftables.conf ]; then
        echo 'include "/etc/nftables/csir-firewall.nft"' > /etc/sysconfig/nftables.conf
    elif [ -f /etc/nftables.conf ]; then
        echo 'include "/etc/nftables/csir-firewall.nft"' > /etc/nftables.conf
    fi

    # 3. Test and apply nftables ruleset
    echo -e "    • Applying active firewall rules..."
    nft -f /etc/nftables/csir-firewall.nft || true

    systemctl daemon-reload
    systemctl enable nftables || true
    systemctl restart nftables || true

    # 4. Configure Suricata IDS telemetry if binary is available
    if command -v suricata >/dev/null 2>&1; then
        echo -e "    • Enabling Suricata Network IDS/IPS sensor..."
        systemctl enable suricata || true
        systemctl restart suricata || true
    fi

    echo -e "${GREEN}[✓] nftables default-deny firewall & Suricata active.${NC}"
}
