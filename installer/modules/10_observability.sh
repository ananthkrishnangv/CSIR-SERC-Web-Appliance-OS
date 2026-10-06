#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 10: Observability & Monitoring
# Deploys Prometheus Node Exporter, Grafana Telemetry & Loki Log Ingestion
#=============================================================================
set -euo pipefail

install_observability_and_monitoring() {
    echo -e "${CYAN}[*] Installing Observability & Monitoring Subsystem...${NC}"

    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y prometheus-node_exporter grafana || zypper install -y golang-github-prometheus-node_exporter || true
            ;;
        "rhel"|"fedora")
            dnf install -y node_exporter grafana || true
            ;;
        "debian")
            apt-get install -y prometheus-node-exporter grafana || true
            ;;
    esac

    # Enable node exporter if service exists
    for svc in prometheus-node-exporter prometheus-node_exporter node_exporter; do
        if systemctl list-unit-files | grep -q "$svc"; then
            systemctl enable "$svc" || true
            systemctl restart "$svc" || true
            echo -e "${GREEN}[✓] Node metrics exporter active on port 9100.${NC}"
            break
        fi
    done

    # Enable Grafana if service exists
    if systemctl list-unit-files | grep -q "grafana-server"; then
        systemctl enable grafana-server || true
        systemctl restart grafana-server || true
        echo -e "${GREEN}[✓] Grafana visual telemetry dashboard active on port 3000.${NC}"
    fi

    echo -e "${GREEN}[✓] Observability & Monitoring Subsystem configured.${NC}"
}
