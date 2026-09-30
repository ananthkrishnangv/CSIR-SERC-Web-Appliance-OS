import json
from pathlib import Path
from typing import Dict, Any, List
from app.config import settings

class SecurityEngineService:
    """
    Manages Web Application Firewall (Coraza + OWASP CRS v4),
    Reverse Proxy configuration (HAProxy), and nftables firewall rules.
    """

    def __init__(self):
        self.conf_dir = settings.DATA_DIR / "security"
        self.conf_dir.mkdir(parents=True, exist_ok=True)

    def generate_haproxy_config(self, apps: List[Dict[str, Any]]) -> str:
        """Generates production-grade HAProxy reverse proxy configuration."""
        cfg = """# CSIR-SWA OS Reverse Proxy Configuration
global
    log /dev/log local0 info
    chroot /var/lib/haproxy
    user haproxy
    group haproxy
    daemon
    stats socket /run/haproxy/admin.sock mode 660 level admin

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend csir_https_in
    bind 0.0.0.0:443 ssl crt /etc/csir-swa/certs/default.pem alpn h2,http/1.1
    mode http
    option forwardfor
    http-request set-header X-Forwarded-Proto https
    http-request set-header X-Appliance-ID CSIR-SWA-01

    # WAF SPOE Hook for Coraza Engine
    filter spoe engine coraza-waf config /etc/coraza/coraza-spoe.conf
    event on-frontend-http-request

"""
        # Add host routing ACLs for each configured application
        for app in apps:
            app_id = app.get("app_id")
            domain = app.get("domain")
            cfg += f"    acl is_app_{app_id} hdr(host) -i {domain}\n"
            cfg += f"    use_backend bk_{app_id} if is_app_{app_id}\n"

        cfg += "\n# Application Upstream Backends\n"
        for app in apps:
            app_id = app.get("app_id")
            port = app.get("port")
            cfg += f"""backend bk_{app_id}
    mode http
    balance roundrobin
    option httpchk GET /health
    server app1 127.0.0.1:{port} check inter 5s rise 2 fall 3
"""

        file_path = self.conf_dir / "haproxy.cfg"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cfg)
        return str(file_path)

    def generate_nftables_rules(self, open_ports: List[int] = None) -> str:
        """Generates default-deny nftables firewall rules."""
        open_ports = open_ports or [80, 443, 8443]
        ports_str = ", ".join(str(p) for p in open_ports)

        nft = f"""#!/usr/sbin/nft -f
# CSIR-SWA OS Default-Deny Host Firewall Ruleset
flush ruleset

table inet csir_filter {{
    chain input {{
        type filter hook input priority filter; policy drop;

        # Allow established and related traffic
        ct state established,related accept

        # Allow loopback interface
        iif "lo" accept

        # Allow ICMP echo with rate limiting
        ip protocol icmp icmp type echo-request limit rate 5/second accept

        # Allow authorized ingress ports (HTTP, HTTPS, Management Portal)
        tcp dport {{ {ports_str} }} accept

        # Drop and log rest
        log prefix "NFTABLES-DROP: " flags all drop
    }}

    chain forward {{
        type filter hook forward priority filter; policy drop;
    }}

    chain output {{
        type filter hook output priority filter; policy accept;
    }}
}}
"""
        file_path = self.conf_dir / "csir-firewall.nft"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(nft)
        return str(file_path)

    def parse_suricata_eve_alert(self, raw_line: str) -> Dict[str, Any]:
        """Parses a Suricata EVE JSON alert entry into structured event."""
        try:
            data = json.loads(raw_line)
            alert = data.get("alert", {})
            return {
                "source_ip": data.get("src_ip", "0.0.0.0"),
                "dest_ip": data.get("dest_ip", "0.0.0.0"),
                "signature": alert.get("signature", "Unknown"),
                "category": alert.get("category", "General Security Alert"),
                "severity": alert.get("severity", 3),
                "timestamp": data.get("timestamp")
            }
        except Exception:
            return {"error": "Invalid EVE JSON log format"}

security_engine = SecurityEngineService()
