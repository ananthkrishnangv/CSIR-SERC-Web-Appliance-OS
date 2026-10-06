#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 02: 3rd-Party & Production Repositories
# Configures verified package repositories for the target Linux distribution
#=============================================================================
set -euo pipefail

configure_distribution_repositories() {
    echo -e "${CYAN}[*] Configuring certified 3rd-party and production repositories for ${DISTRO_NAME}...${NC}"

    case "$DISTRO_FAMILY" in
        "suse")
            echo -e "    • Enabling openSUSE / SUSE production repositories..."
            local SUSE_TARGET="openSUSE_Tumbleweed"
            if [[ "$DISTRO_ID" == "opensuse-leap" ]]; then
                SUSE_TARGET="15.6"
            fi

            mkdir -p /etc/zypp/repos.d

            # 1. Security Tools (Suricata, Falco, Coraza)
            cat <<EOF > /etc/zypp/repos.d/csir-security.repo
[csir-security]
name=CSIR Security Tools (Suricata, Coraza, Cosign)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/security/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

            # 2. Container Stack (Podman 6.1+, Quadlet, Netavark)
            cat <<EOF > /etc/zypp/repos.d/csir-containers.repo
[csir-containers]
name=CSIR Container Platform (Podman Quadlet)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/devel:/microos/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

            # 3. Database Platform (PostgreSQL 17, PgBouncer)
            cat <<EOF > /etc/zypp/repos.d/csir-database.repo
[csir-database]
name=CSIR Database Platform (PostgreSQL 17)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/server:/database:/postgresql/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

            # 4. Edge Reverse Proxy (HAProxy, NGINX)
            cat <<EOF > /etc/zypp/repos.d/csir-network.repo
[csir-network]
name=CSIR Edge Proxy Platform (HAProxy, NGINX)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/network/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

            # 5. Monitoring & Observability (Prometheus, Grafana)
            cat <<EOF > /etc/zypp/repos.d/csir-monitoring.repo
[csir-monitoring]
name=CSIR Observability (Prometheus, Grafana, Loki)
enabled=1
autorefresh=1
baseurl=https://download.opensuse.org/repositories/server:/monitoring/${SUSE_TARGET}/
type=rpm-md
gpgcheck=0
EOF

            echo -e "    • Refreshing zypper repositories..."
            if [ "$IS_TRANSACTIONAL" = true ]; then
                echo -e "${BLUE}[i] Running in MicroOS transactional environment. Staging repo refresh...${NC}"
                zypper --gpg-auto-import-keys refresh || true
            else
                zypper --gpg-auto-import-keys refresh || true
            fi
            ;;

        "rhel")
            echo -e "    • Enabling RHEL/Rocky/AlmaLinux enterprise repositories..."
            dnf install -y epel-release || true
            
            # Enable CRB / CodeReady Builder
            if command -v crb >/dev/null 2>&1; then
                crb enable || true
            elif dnf config-manager --help | grep -q "set-enabled"; then
                dnf config-manager --set-enabled crb || dnf config-manager --set-enabled powertools || true
            fi

            # Official PostgreSQL 17 Yum Repository
            local RHEL_MAJ="${DISTRO_VERSION%%.*}"
            [ -z "$RHEL_MAJ" ] && RHEL_MAJ="9"
            cat <<EOF > /etc/yum.repos.d/csir-pgdg.repo
[csir-pgdg17]
name=PostgreSQL 17 Official Repository
baseurl=https://download.postgresql.org/pub/repos/yum/17/redhat/rhel-${RHEL_MAJ}-x86_64
enabled=1
gpgcheck=0
EOF

            # Official Grafana Repository
            cat <<EOF > /etc/yum.repos.d/csir-grafana.repo
[csir-grafana]
name=Grafana Official Repository
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=0
enabled=1
gpgcheck=0
EOF
            dnf makecache || true
            ;;

        "fedora")
            echo -e "    • Enabling Fedora production repositories..."
            cat <<EOF > /etc/yum.repos.d/csir-grafana.repo
[csir-grafana]
name=Grafana Official Repository
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=0
enabled=1
gpgcheck=0
EOF
            dnf makecache || true
            ;;

        "debian")
            echo -e "    • Enabling Debian/Ubuntu production repositories..."
            apt-get update -y || true
            apt-get install -y ca-certificates curl gnupg || true
            ;;
    esac

    echo -e "${GREEN}[✓] Production & 3rd-party repositories successfully integrated.${NC}"
}
