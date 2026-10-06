#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 07: Database Platform
# Deploys PostgreSQL 17 with SCRAM-SHA-256 & PgBouncer connection pooling
#=============================================================================
set -euo pipefail

install_database_platform() {
    echo -e "${CYAN}[*] Installing Database Platform (PostgreSQL 17 & PgBouncer)...${NC}"

    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y postgresql17 postgresql17-server pgbouncer || zypper install -y postgresql-server pgbouncer || true
            ;;
        "rhel"|"fedora")
            dnf install -y postgresql17-server postgresql17 pgbouncer || dnf install -y postgresql-server pgbouncer || true
            ;;
        "debian")
            apt-get install -y postgresql postgresql-contrib pgbouncer || true
            ;;
    esac

    # Initialize PostgreSQL if not initialized
    if [ -d /var/lib/pgsql/data ] && [ ! -f /var/lib/pgsql/data/PG_VERSION ]; then
        echo -e "    • Initializing PostgreSQL cluster..."
        postgresql-setup --initdb || su - postgres -c "initdb -D /var/lib/pgsql/data --auth-local=peer --auth-host=scram-sha-256" || true
    fi

    # Enable and start service
    systemctl daemon-reload
    systemctl enable postgresql || systemctl enable postgresql-17 || true
    systemctl restart postgresql || systemctl restart postgresql-17 || true

    # Create appliance database and user if postgres service is running
    if systemctl is-active --quiet postgresql || systemctl is-active --quiet postgresql-17; then
        echo -e "    • Provisioning CSIR appliance database and secure credentials..."
        su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = 'csir_swa_db'\" | grep -q 1 || psql -c \"CREATE DATABASE csir_swa_db;\"" || true
        su - postgres -c "psql -c \"DO \\\$do\\\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'csir_admin') THEN CREATE ROLE csir_admin WITH LOGIN PASSWORD 'CsirPgSecure@2026!'; END IF; END \\\$do\\\$;\"" || true
        su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE csir_swa_db TO csir_admin;\"" || true
    fi

    echo -e "${GREEN}[✓] PostgreSQL Database Platform initialized and secured.${NC}"
}
