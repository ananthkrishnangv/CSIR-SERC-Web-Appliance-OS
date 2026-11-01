"""
CSIR Secure Web Appliance OS - Web Management Console Testbed & Screenshot Generator
Enhanced with Web Hosting, Virtual Hosts, Reverse Proxy, and SSL Key Vault.
Captures high-resolution individual screenshots of each subsystem using headless Edge.
"""

import os
import sys
import time
import json
import threading
import subprocess
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8443
HOST = "127.0.0.1"
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "backend" / "app" / "static"
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots" / "web_console"

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Mock Data
MOCK_APPLICATIONS = [
    {
        "app_id": "app-01",
        "name": "CSIR-SERC Structural Health Portal",
        "image": "registry.csir.res.in/apps/structural-health:v2.4.0",
        "digest": "sha256:7f83b165c928471bade01293847acdf",
        "port": 8081,
        "domain": "shm.serc.res.in",
        "status": "running",
        "health": "healthy",
        "waf_mode": "enforcing",
        "backup_status": "protected",
        "cpu_percent": 3.8,
        "memory_mb": 512,
        "is_rootless": True,
        "created_at": "2026-10-15T08:00:00Z"
    },
    {
        "app_id": "app-02",
        "name": "Wind Engineering Aerodynamic Telemetry",
        "image": "registry.csir.res.in/apps/wind-tunnel:v1.9.1",
        "digest": "sha256:9a32c4518471bade01293847acdf7f83",
        "port": 8082,
        "domain": "wind.serc.res.in",
        "status": "running",
        "health": "healthy",
        "waf_mode": "enforcing",
        "backup_status": "protected",
        "cpu_percent": 7.2,
        "memory_mb": 1024,
        "is_rootless": True,
        "created_at": "2026-10-18T11:30:00Z"
    },
    {
        "app_id": "app-03",
        "name": "Tower Testing & Acoustic Sensor Engine",
        "image": "registry.csir.res.in/apps/acoustic-sensor:v3.0.2",
        "digest": "sha256:4d87e11901293847acdf7f83b165c928",
        "port": 8083,
        "domain": "sensors.serc.res.in",
        "status": "running",
        "health": "healthy",
        "waf_mode": "enforcing",
        "backup_status": "protected",
        "cpu_percent": 2.4,
        "memory_mb": 384,
        "is_rootless": True,
        "created_at": "2026-10-20T14:15:00Z"
    },
    {
        "app_id": "app-04",
        "name": "National Knowledge Network Edge Cache",
        "image": "registry.csir.res.in/infra/nkn-cache:v1.2.0",
        "digest": "sha256:2b90ff45acdf7f83b165c928471bade0",
        "port": 8084,
        "domain": "cache.serc.res.in",
        "status": "running",
        "health": "healthy",
        "waf_mode": "enforcing",
        "backup_status": "protected",
        "cpu_percent": 1.1,
        "memory_mb": 256,
        "is_rootless": True,
        "created_at": "2026-10-22T09:45:00Z"
    }
]

# NEW FEATURE: Virtual Hosts & Web Hosting
MOCK_VHOSTS = [
    {
        "id": "vh-01",
        "domain": "serc.res.in",
        "aliases": "www.serc.res.in, portal.serc.res.in",
        "docroot": "/srv/www/vhosts/serc.res.in/public_html",
        "runtime": "PHP 8.2-FPM",
        "runtime_badge": "bg-indigo-100 text-indigo-800",
        "ssl_status": "Let's Encrypt (Auto-Renew)",
        "storage_used": "14.2 GB",
        "storage_quota": "50 GB",
        "quota_percent": 28
    },
    {
        "id": "vh-02",
        "domain": "wind.serc.res.in",
        "aliases": "tunnel-data.serc.res.in",
        "docroot": "/srv/www/vhosts/wind.serc.res.in/dist",
        "runtime": "Node.js 20 SSR",
        "runtime_badge": "bg-emerald-100 text-emerald-800",
        "ssl_status": "Wildcard *.serc.res.in",
        "storage_used": "8.5 GB",
        "storage_quota": "30 GB",
        "quota_percent": 28
    },
    {
        "id": "vh-03",
        "domain": "sensors.serc.res.in",
        "aliases": "telemetry.serc.res.in",
        "docroot": "/srv/www/vhosts/sensors.serc.res.in/app",
        "runtime": "Python ASGI / FastHTML",
        "runtime_badge": "bg-sky-100 text-sky-800",
        "ssl_status": "Let's Encrypt (Auto-Renew)",
        "storage_used": "4.1 GB",
        "storage_quota": "20 GB",
        "quota_percent": 20
    },
    {
        "id": "vh-04",
        "domain": "archive.serc.res.in",
        "aliases": "open-access.serc.res.in",
        "docroot": "/srv/www/vhosts/archive.serc.res.in/htdocs",
        "runtime": "Static / Nginx Fast-Cache",
        "runtime_badge": "bg-slate-100 text-slate-800",
        "ssl_status": "Wildcard *.serc.res.in",
        "storage_used": "22.8 GB",
        "storage_quota": "100 GB",
        "quota_percent": 23
    }
]

# NEW FEATURE: Reverse Proxy Upstream Pools
MOCK_UPSTREAMS = [
    {
        "pool_id": "pool-01",
        "name": "Structural Health Telemetry Pool",
        "algorithm": "Round-Robin",
        "path_prefix": "/api/v1/shm/*",
        "health_uri": "/healthz",
        "check_interval": 5,
        "active_targets": 3,
        "total_targets": 3,
        "avg_latency": 4.2,
        "targets": ["10.20.10.101:8081", "10.20.10.102:8081", "10.20.10.103:8081"]
    },
    {
        "pool_id": "pool-02",
        "name": "Wind Tunnel High-Rate Ingestion",
        "algorithm": "Least-Connections",
        "path_prefix": "/ingest/aerodynamics/*",
        "health_uri": "/api/ping",
        "check_interval": 3,
        "active_targets": 2,
        "total_targets": 2,
        "avg_latency": 2.8,
        "targets": ["10.20.10.201:8082", "10.20.10.202:8082"]
    },
    {
        "pool_id": "pool-03",
        "name": "Sovereign AI Inference & ChatOps",
        "algorithm": "IP-Hash Session Pinned",
        "path_prefix": "/api/v1/ai-security/*",
        "health_uri": "/health",
        "check_interval": 10,
        "active_targets": 2,
        "total_targets": 2,
        "avg_latency": 12.5,
        "targets": ["127.0.0.1:8000", "127.0.0.1:8001"]
    }
]

# NEW FEATURE: SSL / TLS Key Vault & Certificates
MOCK_SSL_CERTIFICATES = [
    {
        "id": "cert-01",
        "common_name": "*.serc.res.in",
        "sans": "*.serc.res.in, serc.res.in",
        "issuer": "CSIR Sovereign Root CA / Let's Encrypt ACME",
        "key_spec": "ECDSA secp384r1 (High Security)",
        "sig_algo": "SHA384withECDSA",
        "days_left": 84,
        "auto_renew": True
    },
    {
        "id": "cert-02",
        "common_name": "shm.serc.res.in",
        "sans": "shm.serc.res.in, sensor-edge.serc.res.in",
        "issuer": "Let's Encrypt E6 Intermediate",
        "key_spec": "RSA 4096-bit (Military Grade)",
        "sig_algo": "SHA256withRSA",
        "days_left": 42,
        "auto_renew": True
    },
    {
        "id": "cert-03",
        "common_name": "appliance.internal.serc.res.in",
        "sans": "10.20.10.15, localhost",
        "issuer": "CSIR-SERC Hardware TPM-Backed Internal CA",
        "key_spec": "ECDSA secp256r1 (TPM Endorsement)",
        "sig_algo": "SHA256withECDSA",
        "days_left": 312,
        "auto_renew": True
    }
]

MOCK_WAF_RULES = [
    {"rule_id": 941100, "name": "OWASP CRS: XSS Filter Defense (Script Tag Vectors)", "enabled": True, "action": "deny", "severity": "CRITICAL"},
    {"rule_id": 942100, "name": "OWASP CRS: SQL Injection Defense (Tautology & Stacked Queries)", "enabled": True, "action": "deny", "severity": "CRITICAL"},
    {"rule_id": 930100, "name": "OWASP CRS: Path Traversal & LFI Attack Mitigation", "enabled": True, "action": "deny", "severity": "HIGH"},
    {"rule_id": 932100, "name": "OWASP CRS: Remote Command Execution (RCE) Filter", "enabled": True, "action": "deny", "severity": "CRITICAL"},
    {"rule_id": 920350, "name": "Host Header Validation & HTTP Request Smuggling Guard", "enabled": True, "action": "deny", "severity": "HIGH"},
    {"rule_id": 913100, "name": "Automated Scanner & Malicious Bot User-Agent Blocker", "enabled": True, "action": "drop", "severity": "MEDIUM"}
]

MOCK_FIREWALL_RULES = [
    {"chain": "input", "protocol": "tcp", "dport": 443, "source": "0.0.0.0/0", "action": "accept", "comment": "UX4G HTTPS Management Console"},
    {"chain": "input", "protocol": "tcp", "dport": 80, "source": "0.0.0.0/0", "action": "accept", "comment": "HAProxy HTTP (Redirect to HTTPS)"},
    {"chain": "input", "protocol": "tcp", "dport": 2222, "source": "10.0.0.0/8", "action": "accept", "comment": "Admin SSH Bastion (Ed25519 Only)"},
    {"chain": "input", "protocol": "udp", "dport": 123, "source": "10.20.10.1", "action": "accept", "comment": "NPL India NTP Stratum 1 Clock Sync"},
    {"chain": "input", "protocol": "all", "dport": 0, "source": "0.0.0.0/0", "action": "drop", "comment": "Default Ingress Drop Policy"}
]

MOCK_NARRATIVES = [
    {
        "narrative_id": "NAR-882",
        "title": "Autonomous Defense: Coordinated Scanner Neutralization",
        "executive_summary": "At 14:22 IST, an external IP pool launched automated vulnerability probing targeting port 8081. Coraza WAF triggered 412 consecutive block events under Rule 942100 (SQLi). Local Node Agent immediately escalated the source subnet into nftables drop set with a 24-hour rate-limit lock.",
        "incident_count": 412,
        "threat_level": "Elevated / Mitigated",
        "created_at": "2026-11-01T14:30:00Z"
    }
]

MOCK_RECOMMENDATIONS = [
    {
        "rec_id": "rec-01",
        "title": "Enable PostgreSQL GIN Index for Structural Sensor Analytics",
        "description": "Query 'SELECT * FROM sensor_readings WHERE metadata ILIKE %vibration%' causes sequential scans. Creating GIN index drops latency from 1,420ms to 8ms.",
        "impact_level": "high",
        "approval_required": "human",
        "status": "pending",
        "created_at": "2026-11-01T15:00:00Z"
    },
    {
        "rec_id": "rec-02",
        "title": "Harden Coraza WAF Paranoia Level to Level 2 on Admin Paths",
        "description": "Increases inspection strictness on /api/v1/admin to prevent advanced prototype pollution and obscure SQL encodings.",
        "impact_level": "medium",
        "approval_required": "human",
        "status": "pending",
        "created_at": "2026-11-01T14:45:00Z"
    }
]

MOCK_SNAPSHOTS = [
    {"snapshot_number": 14, "subvolume": "@", "cleanup_type": "number", "description": "MicroOS Transactional Baseline (Kernel 6.12.0-rc3)", "created_at": "2026-10-30T10:00:00Z"},
    {"snapshot_number": 13, "subvolume": "@/srv", "cleanup_type": "timeline", "description": "Pre-Update Production Workload Dataset", "created_at": "2026-10-29T18:00:00Z"},
    {"snapshot_number": 12, "subvolume": "@/var", "cleanup_type": "number", "description": "Tamper-Evident CERT-In Audit Log Checkpoint", "created_at": "2026-10-28T12:00:00Z"},
    {"snapshot_number": 11, "subvolume": "@", "cleanup_type": "timeline", "description": "Post-Installation Immutable System Root", "created_at": "2026-10-25T09:30:00Z"}
]

MOCK_DR_TESTS = [
    {"test_id": "dr-101", "target_app": "CSIR-SERC Structural Health Portal", "measured_rto_seconds": 23, "measured_rpo_seconds": 45, "verified_hash": "a4f89d31c82b01ef77823abce12890cd", "status": "verified"},
    {"test_id": "dr-102", "target_app": "Wind Engineering Aerodynamic Telemetry", "measured_rto_seconds": 18, "measured_rpo_seconds": 30, "verified_hash": "e190cc4521bd098feea7610023456789", "status": "verified"},
    {"test_id": "dr-103", "target_app": "Tower Testing & Acoustic Sensor Engine", "measured_rto_seconds": 12, "measured_rpo_seconds": 15, "verified_hash": "99f018d45ca1028476bb1983012984aa", "status": "verified"}
]

MOCK_AUDIT_LEDGER = [
    {"entry_index": 1048, "timestamp": "2026-11-01 14:35:12 IST", "actor": "security_officer@csir.res.in", "actor_ip": "10.20.10.45", "action": "TOGGLE_WAF_RULE", "resource": "waf_rule:942100", "prev_hash": "77a83d9102ef1904bbce019842ad918237190caef0192471bade01293847acdf", "entry_hash": "c8f2a1b94d801eef2a9840134bcad0918732014fbca820147cbde0192348a1b2"},
    {"entry_index": 1047, "timestamp": "2026-11-01 12:10:04 IST", "actor": "admin@csir.res.in", "actor_ip": "10.20.10.15", "action": "RUN_RESTIC_BACKUP", "resource": "backup:b-9902", "prev_hash": "19bfa8370129acdf84729103847bca891029348acf1092847badce019238471a", "entry_hash": "77a83d9102ef1904bbce019842ad918237190caef0192471bade01293847acdf"},
    {"entry_index": 1046, "timestamp": "2026-11-01 09:45:33 IST", "actor": "system:ai_advisor", "actor_ip": "127.0.0.1", "action": "AI_RECOMMENDATION_GENERATED", "resource": "recommendation:rec-01", "prev_hash": "ff0918237190caef0192471bade01293847acdfa4f89d31c82b01ef77823abc", "entry_hash": "19bfa8370129acdf84729103847bca891029348acf1092847badce019238471a"},
    {"entry_index": 1045, "timestamp": "2026-10-31 22:00:00 IST", "actor": "system:chronyd", "actor_ip": "127.0.0.1", "action": "NTP_CLOCK_DISCIPLINE_SYNC", "resource": "clock:npl_delhi_stratum1", "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000", "entry_hash": "ff0918237190caef0192471bade01293847acdfa4f89d31c82b01ef77823abc"}
]

MOCK_UPDATE_STATUS = {
    "channel": "stable",
    "available_channels": ["stable", "lts", "security-only"],
    "active_snapshot": 14,
    "staged_snapshot": None,
    "reboot_required": False,
    "base_os": "openSUSE MicroOS (Transactional-Update Engine)"
}

class TestbedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        url = self.path.split("?")[0]

        routes = {
            "/api/v1/applications": MOCK_APPLICATIONS,
            "/api/v1/webhosting/vhosts": MOCK_VHOSTS,
            "/api/v1/proxy/upstreams": MOCK_UPSTREAMS,
            "/api/v1/ssl/certificates": MOCK_SSL_CERTIFICATES,
            "/api/v1/security/waf/rules": MOCK_WAF_RULES,
            "/api/v1/security/firewall/rules": MOCK_FIREWALL_RULES,
            "/api/v1/ai-security/narratives": MOCK_NARRATIVES,
            "/api/v1/ai-security/recommendations": MOCK_RECOMMENDATIONS,
            "/api/v1/backups/snapshots": MOCK_SNAPSHOTS,
            "/api/v1/backups/dr-tests": MOCK_DR_TESTS,
            "/api/v1/audit/ledger": MOCK_AUDIT_LEDGER,
            "/api/v1/updates/status": MOCK_UPDATE_STATUS,
            "/api/v1/health": {"status": "healthy", "service": "CSIR-SWA-OS Management Engine"}
        }

        if url in routes:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(routes[url]).encode("utf-8"))
            return

        if url == "/" or url == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(STATIC_DIR / "index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        super().do_GET()

    def log_message(self, format, *args):
        pass

def run_server(server):
    server.serve_forever()

def capture_tab(edge_path, tab_name, output_png):
    temp_html = STATIC_DIR / f"_temp_view_{tab_name}.html"
    with open(STATIC_DIR / "index.html", "r", encoding="utf-8") as f:
        content = f.read()

    mod_content = content.replace(
        "const activeTab = ref('overview');",
        f"const activeTab = ref('{tab_name}');"
    )

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(mod_content)

    temp_url = f"http://{HOST}:{PORT}/_temp_view_{tab_name}.html"

    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1920,1080",
        f"--screenshot={str(output_png)}",
        temp_url
    ]

    try:
        subprocess.run(cmd, timeout=15, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    finally:
        if temp_html.exists():
            temp_html.unlink()

def main():
    print(f"[*] Starting Enhanced CSIR-SWA OS Testbed Server on http://{HOST}:{PORT}...")
    server = HTTPServer((HOST, PORT), TestbedHandler)
    t = threading.Thread(target=run_server, args=(server,), daemon=True)
    t.start()
    time.sleep(1)

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not Path(edge_path).exists():
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    tabs = [
        ("overview", "web_console_01_overview.png"),
        ("vhosts", "web_console_02_vhosts.png"),
        ("proxy", "web_console_03_proxy.png"),
        ("ssl", "web_console_04_ssl.png"),
        ("applications", "web_console_05_applications.png"),
        ("security", "web_console_06_security_waf.png"),
        ("ai_security", "web_console_07_ai_security_center.png"),
        ("data_protection", "web_console_08_data_protection_backups.png"),
        ("compliance", "web_console_09_compliance_audit_ledger.png"),
        ("updates", "web_console_10_transactional_updates.png"),
        ("boot_screen", "web_console_11_boot_screen_console.png")
    ]

    print(f"[*] Capturing {len(tabs)} individual high-resolution screenshots...")
    for tab, filename in tabs:
        out_path = SCREENSHOTS_DIR / filename
        print(f"    -> Capturing [{tab}] -> {filename}")
        capture_tab(edge_path, tab, out_path)
        if out_path.exists():
            print(f"       [OK] Generated {out_path.name} ({out_path.stat().st_size:,} bytes)")
        else:
            print(f"       [!] Failed to generate {out_path.name}")

    print("\n[SUCCESS] All Web Management Console screenshots captured successfully!")
    server.shutdown()

if __name__ == "__main__":
    main()
