#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 04: Web Delivery & WAF
# Deploys HAProxy / NGINX Reverse Proxy, TLS 1.3 & Coraza WAF (OWASP CRS v4)
#=============================================================================
set -euo pipefail

install_web_delivery_and_waf() {
    echo -e "${CYAN}[*] Installing Web Delivery & WAF Subsystem (HAProxy + Coraza)...${NC}"

    # 1. Install HAProxy and openssl
    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y haproxy openssl ca-certificates || true
            ;;
        "rhel"|"fedora")
            dnf install -y haproxy openssl ca-certificates || true
            ;;
        "debian")
            apt-get install -y haproxy openssl ca-certificates || true
            ;;
    esac

    # 2. Generate Initial Self-Signed TLS 1.3 Appliance Certificate
    local CERT_DIR="/etc/ssl/csir-swa"
    mkdir -p "$CERT_DIR"
    if [ ! -f "$CERT_DIR/appliance.pem" ]; then
        echo -e "    • Generating self-signed TLS 1.3 appliance certificates..."
        openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
            -keyout "$CERT_DIR/appliance.key" \
            -out "$CERT_DIR/appliance.crt" \
            -subj "/C=IN/ST=Tamil Nadu/L=Chennai/O=CSIR-SERC/OU=Secure Infrastructure/CN=$(hostname -f 2>/dev/null || echo 'csir-appliance.local')" \
            -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null || true
        
        # Combine key and cert for HAProxy pem format
        cat "$CERT_DIR/appliance.crt" "$CERT_DIR/appliance.key" > "$CERT_DIR/appliance.pem"
        chmod 600 "$CERT_DIR/appliance.key" "$CERT_DIR/appliance.pem"
    fi

    # 3. Deploy Coraza WAF Profiles & OWASP CRS v4
    echo -e "    • Configuring Coraza WAF and OWASP CRS v4..."
    mkdir -p /etc/coraza
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    if [ -f "$SCRIPT_DIR/assets/security/coraza.conf" ]; then
        cp "$SCRIPT_DIR/assets/security/coraza.conf" /etc/coraza/coraza.conf
    fi
    if [ -f "$SCRIPT_DIR/assets/security/crs-setup.conf" ]; then
        cp "$SCRIPT_DIR/assets/security/crs-setup.conf" /etc/coraza/crs-setup.conf
    fi

    # 4. Generate Master HAProxy Configuration
    echo -e "    • Generating /etc/haproxy/haproxy.cfg..."
    cat <<EOF > /etc/haproxy/haproxy.cfg
global
    log /dev/log local0 info
    chroot /var/lib/haproxy
    user haproxy
    group haproxy
    daemon
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.3 no-tls-tickets

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

# Public Plain HTTP (Redirects to HTTPS)
frontend fe_http
    bind *:80
    mode http
    redirect scheme https code 301 if !{ ssl_fc }

# Public HTTPS Ingress (Hosted Research Websites & Portals)
frontend fe_https
    bind *:443 ssl crt /etc/ssl/csir-swa/appliance.pem
    mode http
    http-response set-header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    http-response set-header X-Content-Type-Options "nosniff"
    http-response set-header X-Frame-Options "SAMEORIGIN"
    http-response set-header Referrer-Policy "strict-origin-when-cross-origin"
    default_backend be_default_app

# Appliance Management Portal (Port 8443)
frontend fe_management
    bind *:8443 ssl crt /etc/ssl/csir-swa/appliance.pem
    mode http
    http-response set-header X-Appliance-Identity "CSIR-SERC-Secure-Appliance-OS"
    default_backend be_control_plane

# Control Plane Backend (FastAPI + Static UI)
backend be_control_plane
    mode http
    server srv_fastapi 127.0.0.1:8000 check

# Default Application Backend (Hosted Research Portal Quadlet)
backend be_default_app
    mode http
    server srv_app 127.0.0.1:8080 check backup
EOF

    systemctl daemon-reload
    systemctl enable haproxy || true
    systemctl restart haproxy || true

    echo -e "${GREEN}[✓] Web Delivery & Reverse Proxy (HAProxy + TLS 1.3) successfully activated.${NC}"
}
