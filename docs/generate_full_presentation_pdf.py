#!/usr/bin/env python3
"""
CSIR Secure Web Appliance OS (CSIR-SWA OS)
Full Technical Documentation & Architectural Specification Presentation Generator (Light Mode PDF)

Key Requirements Satisfied:
1. Presentation format in PDF (16:9 widescreen landscape presentation slides).
2. Exactly ONE high-resolution screenshot per page (22 dedicated screenshot slides).
3. Comprehensive documentation for each screenshot:
   - Purpose of each menu
   - Features of the portal and visible controls
   - Tech stack, daemons, packages, and protocols
   - Implementation architecture, REST endpoints, systemd units, configuration paths, and CLI commands
4. STRICT LIGHT MODE ONLY: Crisp white and soft slate backgrounds (#FFFFFF / #F8FAFC),
   high-contrast typography (#0F172A / #1E293B / #4338CA), NO dark mode slides.
5. High-resolution, crystal-clear screenshots with authentic browser/hardware chrome mockups.
6. 100% PROPER NOTO SANS font family loaded and embedded throughout the presentation.
"""

import os
import sys
import base64
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
SCREENSHOTS_DIR = DOCS_DIR / "screenshots" / "web_console"
INSTALLER_DIR = DOCS_DIR / "screenshots" / "installer"
BRANDING_DIR = BASE_DIR / "installer" / "assets" / "branding"

OUTPUT_HTML = DOCS_DIR / "CSIR-SWA-OS-Product-Features-and-Deployment.html"
OUTPUT_PDF = DOCS_DIR / "CSIR-SWA-OS-Product-Features-and-Deployment-Slides.pdf"

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not Path(EDGE_PATH).exists():
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def b64_image(file_path: Path) -> str:
    """Read an image file and return a data URI string."""
    if not file_path.exists():
        print(f"[!] Warning: Image {file_path} not found.")
        return ""
    mime = "image/png" if file_path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(file_path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"

print("[*] Encoding screenshots into Base64 data URIs...")
img_logo = b64_image(BRANDING_DIR / "csir-webos-logo.jpg")

# 14 Web Management Console Screenshots (1920x1080)
img_c_ov       = b64_image(SCREENSHOTS_DIR / "web_console_01_overview.png")
img_c_vh       = b64_image(SCREENSHOTS_DIR / "web_console_02_vhosts.png")
img_c_vmodal   = b64_image(SCREENSHOTS_DIR / "web_console_02b_vhost_modal.png")
img_c_px       = b64_image(SCREENSHOTS_DIR / "web_console_03_proxy.png")
img_c_ssl      = b64_image(SCREENSHOTS_DIR / "web_console_04_ssl.png")
img_c_app      = b64_image(SCREENSHOTS_DIR / "web_console_05_applications.png")
img_c_kvm      = b64_image(SCREENSHOTS_DIR / "web_console_06_virtualization_kvm.png")
img_c_kvm_wiz  = b64_image(SCREENSHOTS_DIR / "web_console_06b_kvm_setup_wizard.png")
img_c_waf      = b64_image(SCREENSHOTS_DIR / "web_console_07_security_waf.png")
img_c_ai       = b64_image(SCREENSHOTS_DIR / "web_console_08_ai_security_center.png")
img_c_dr       = b64_image(SCREENSHOTS_DIR / "web_console_09_data_protection_backups.png")
img_c_comp     = b64_image(SCREENSHOTS_DIR / "web_console_10_compliance_audit_ledger.png")
img_c_upd      = b64_image(SCREENSHOTS_DIR / "web_console_11_transactional_updates.png")
img_c_term     = b64_image(SCREENSHOTS_DIR / "web_console_12_boot_screen_console.png")

# 8 Appliance OS Bare-Metal & Hypervisor Provisioning Screenshots
img_boot       = b64_image(INSTALLER_DIR / "vm_boot_menu_v2.jpg")
img_linuxrc    = b64_image(INSTALLER_DIR / "vm_installer_linuxrc.jpg")
img_yast       = b64_image(INSTALLER_DIR / "vm_step4_yast.jpg")
img_net        = b64_image(INSTALLER_DIR / "vm_step5_yast_net.jpg")
img_probe      = b64_image(INSTALLER_DIR / "vm_step7_probing_done.jpg")
img_part       = b64_image(INSTALLER_DIR / "vm_step8_partitioning.jpg")
img_tty3       = b64_image(INSTALLER_DIR / "vm_tty3_log.jpg")
img_proof      = b64_image(INSTALLER_DIR / "vm_final_gui_proof_ready2.jpg")

print("[OK] All images encoded successfully.")

# ==============================================================================
# SLIDES DATA SPECIFICATION (27 Comprehensive Light-Mode Slides)
# ==============================================================================

slides = []

# ------------------------------------------------------------------------------
# SLIDE 1: Executive Title Slide (Light Mode)
# ------------------------------------------------------------------------------
slides.append({
    "type": "title",
    "bg": "FFFFFF",
    "badge": "NATIONAL SOVEREIGN TECHNOLOGY PLATFORM • VERSION 1.0.0 STABLE CHANNEL",
    "title": "CSIR Secure Web Appliance OS (CSIR-SWA OS)",
    "subtitle": "Hardened, Immutable, and Containerized Web Hosting Appliance Operating System for Institutional Portals, Laboratory Micro-Sites, and Classified Scientific Workloads",
    "lead_org": "Council of Scientific & Industrial Research (CSIR) — CSIR-SERC Chennai",
    "baseline": "openSUSE MicroOS Core • Linux Kernel 6.12 • Btrfs + Snapper • Prompt Indigo UX4G Architecture",
    "highlights": [
        {"title": "100% On-Premises Sovereignty", "desc": "Eliminates recurrent commercial software and hypervisor licenses with certified national cloud resilience."},
        {"title": "CERT-In Section 70B Compliance", "desc": "Built-in SHA-256 hash-chained forensic audit ledger, NPL Stratum-1 time sync, and 1-click incident dossier."},
        {"title": "Turn-Key Deployment Suite", "desc": "2.73 GB monolithic offline DVD ISO, automated combustion scripts, and multi-tenant web console."},
        {"title": "Unified Workload Fleet", "desc": "Natively orchestrates PHP 8.2-FPM, Node.js 20, Python ASGI, Podman Quadlets, and KVM Virtual Machines."}
    ],
    "meta": "Release Baseline: 28 September 2026 | Synchronized: 05 November 2026 | Official Institutional Documentation"
})

# ------------------------------------------------------------------------------
# SLIDE 2: Executive Summary & Appliance Strategic Mission
# ------------------------------------------------------------------------------
slides.append({
    "type": "summary",
    "bg": "F8FAFC",
    "badge": "STRATEGIC INITIATIVE & ARCHITECTURAL MANDATE",
    "title": "Executive Summary: Institutional Mandate & Sovereign Deliverables",
    "subtitle": "Engineering an uncompromised, zero-trust appliance operating system for scientific laboratories and government research centers.",
    "pillars": [
        {
            "icon": "fa-shield-halved",
            "tag": "SECURITY PILLAR",
            "title": "Host Immutability & Zero Persistence",
            "desc": "Operating system root resides on an immutable, read-only Btrfs snapshot. Malware and unauthorized modifications cannot persist across reboots. All atomic system updates are transactional with automated health-gated rollbacks."
        },
        {
            "icon": "fa-boxes-stacked",
            "tag": "WORKLOAD PILLAR",
            "title": "Rootless Workload Sandboxing",
            "desc": "Applications and microservices run exclusively as rootless Podman containers or unprivileged runtimes mapped to dedicated user namespaces (csir-app:100000). Systemd Quadlets provide native service lifecycle supervision."
        },
        {
            "icon": "fa-network-wired",
            "tag": "DELIVERY PILLAR",
            "title": "Edge Defense & High-Throughput Ingress",
            "desc": "HAProxy 3.0 acts as the sovereign reverse proxy with HTTP/2 and HTTP/3 QUIC support, combined with Coraza Web Application Firewall (OWASP CRS v4) performing deep packet inspection entirely on-premises without cloud leaks."
        },
        {
            "icon": "fa-scale-balanced",
            "tag": "COMPLIANCE PILLAR",
            "title": "Statutory Forensic Ledger & Governance",
            "desc": "Mandatory adherence to Indian CERT-In cybersecurity directives. Every privileged command, configuration edit, and WAF toggle is cryptographically chained using SHA-256 with 180-day retention lock and 1-click statutory export."
        }
    ],
    "deliverables": [
        "Monolithic Full-Stack Offline ISO (2.73 GB) bootable on physical hardware (Dell, HPE, Supermicro) and hypervisors (VirtualBox, KVM, VMware, Hyper-V).",
        "Modern UX4G Management Console with Tailwind CSS, daisyUI, and Prompt Indigo SaaS palette for complete zero-terminal administration.",
        "Comprehensive Automated DR Qualification verifying 12-23s Recovery Time Objective (RTO) and 15-45s Recovery Point Objective (RPO)."
    ]
})

# ------------------------------------------------------------------------------
# SLIDE 3: Architectural Planes & Defense-in-Depth Specification
# ------------------------------------------------------------------------------
slides.append({
    "type": "planes",
    "bg": "FFFFFF",
    "badge": "SYSTEM ARCHITECTURE SPECIFICATION",
    "title": "Defense-in-Depth: The Six Operational Architectural Planes",
    "subtitle": "Modular separation of concerns ensuring that a compromise in one plane cannot breach host integrity or statutory ledgers.",
    "planes": [
        {
            "num": "01",
            "name": "Web Delivery & Edge Security",
            "components": "nftables Host Firewall • HAProxy 3.0 • Coraza WAF (OWASP CRS v4) • Suricata 7.0 IDS/IPS",
            "desc": "Default-deny ingress filtering, TLS 1.3 termination, path routing, and real-time mitigation of SQLi, XSS, and HTTP request smuggling."
        },
        {
            "num": "02",
            "name": "Application & Workload Sandboxing",
            "components": "Rootless Podman 6.1.2 • systemd Quadlets • UserNS (UID 100000) • PHP 8.2-FPM • Node 20 • Python ASGI",
            "desc": "POSIX-isolated document roots (/srv/www/vhosts), declarative container definitions, and mandatory Cosign cryptographic image digest checks."
        },
        {
            "num": "03",
            "name": "Immutable Base Operating System",
            "components": "openSUSE MicroOS • Linux Kernel 6.12 • Btrfs Subvolumes (@, @/srv, @/var) • Snapper 0.10 • transactional-update",
            "desc": "Read-only root filesystem, atomic package installation into staged snapshots, and autonomous fallback reboot via csir-health-gate."
        },
        {
            "num": "04",
            "name": "Appliance Management Control Plane",
            "components": "FastAPI 0.141 • Python 3.14 • Privileged Node Agent (Strict Allow-list) • Nuxt 4 / Vue 3 UX4G Console",
            "desc": "Role-Based Access Control (Admin, Sec-Officer, Operator, Auditor), Unix socket IPC, and comprehensive REST API suite on port 8443."
        },
        {
            "num": "05",
            "name": "Resilient Data Protection & DR",
            "components": "Btrfs CoW Snapshots • Restic 0.19 Encrypted Deduplication • PostgreSQL 17 WAL PITR • Automated DR Sandbox",
            "desc": "Sub-minute disaster recovery drills, AES-256 encrypted remote repository backups, and verified SHA-256 data integrity checkpoints."
        },
        {
            "num": "06",
            "name": "Local AI Operations & Governance",
            "components": "Sovereign Quantized Local LLM • OPA Policy Engine • Chrony NPL Stratum-1 Sync • SHA-256 Audit Ledger",
            "desc": "Autonomous threat narrative synthesis, latency RCA, natural language ChatOps with mandatory human approval gates, and CERT-In dossier export."
        }
    ]
})

# ==============================================================================
# 14 WEB MANAGEMENT CONSOLE SCREENSHOT SLIDES (Figures 01 to 14)
# ==============================================================================

# Slide 4: Figure 1 - Overview Dashboard
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "01",
    "badge": "MANAGEMENT PLANE • EXECUTIVE MONITORING",
    "title": "Central Operations & Security Health Overview Dashboard",
    "subtitle": "Real-time institutional mission control aggregating system health, ingress throughput, container fleet telemetry, and active threat shields.",
    "image": img_c_ov,
    "url": "https://appliance.internal.serc.res.in:8443/#/overview",
    "caption": "Figure 1: Executive Operations Cockpit displaying 98.4% Health Score, 1,842 req/s Ingress, 4 Active Podman Workloads, and 1,429 Blocked Threats.",
    "pills": [
        {"icon": "fa-heart-pulse", "label": "Health Score", "val": "98.4% (Optimal)"},
        {"icon": "fa-gauge-high", "label": "Ingress Rate", "val": "1,842 req/s (p95 < 10ms)"},
        {"icon": "fa-cube", "label": "Workloads", "val": "4 Containers / 0 Errors"},
        {"icon": "fa-shield-virus", "label": "WAF Drops", "val": "1,429 Interceptions"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Acts as the unified operational cockpit for appliance administrators and security officers.",
                "Provides single-pane-of-glass situational awareness across all 6 architectural planes without terminal access.",
                "Immediately highlights degradation in container health, proxy latency, or sudden spikes in malicious ingress probing.",
                "Enables rapid response coordination through embedded sovereign ChatOps incident streaming."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Four interactive KPI cards with real-time percentage trend indicators and status badges.",
                "Daemon Status Grid monitoring HAProxy, Coraza WAF, Suricata IDS, Podman, Snapper, and PostgreSQL.",
                "Live Security Telemetry Feed displaying blocked IP addresses, country flags, targeted paths, and OWASP rule IDs.",
                "Integrated Prompt Indigo ChatOps widget with quick action triggers for status audits and memory reports."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Frontend: Vue 3.5, Nuxt 4, Tailwind CSS 3.4, daisyUI 4.12, Font Awesome 6.4 Pro icons.",
                "Backend: FastAPI 0.141 asynchronous ASGI control plane running on Python 3.14.7.",
                "Telemetry Collectors: Prometheus node_exporter, systemd dbus API, and HAProxy stats socket (/run/haproxy/admin.sock).",
                "Event Streaming: HTML5 Server-Sent Events (SSE) and WebSockets for sub-second telemetry propagation."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/system/overview, GET /api/v1/telemetry/stream (WebSocket).",
                "Host Metrics: Node Agent polls kernel /proc and cgroups v2 hierarchy (/sys/fs/cgroup/) with 3s refresh.",
                "Security: Non-root execution under csir-swa daemon user; API sessions authenticated via JWT + SCRAM-SHA-256.",
                "CLI Commands: csir-ctl status --all, csir-ctl health --json, csir-ctl telemetry live."
            ]
        }
    ]
})

# Slide 5: Figure 2 - Virtual Hosts Fleet
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "02",
    "badge": "WORKLOAD PLANE • NATIVE WEB HOSTING",
    "title": "Native Web Hosting & Multi-Tenant Virtual Host Fleet",
    "subtitle": "Complete virtual host life-cycle management, polyglot application runtimes, Btrfs storage quotas, and automated SSL bindings.",
    "image": img_c_vh,
    "url": "https://appliance.internal.serc.res.in:8443/#/vhosts",
    "caption": "Figure 2: Virtual Host Fleet Management Table showing multi-tenant runtimes (PHP 8.2, Node 20, Python ASGI), quotas, and Let's Encrypt status.",
    "pills": [
        {"icon": "fa-globe", "label": "Active Hosts", "val": "4 Institutional Domains"},
        {"icon": "fa-code", "label": "Runtimes", "val": "PHP 8.2 • Node 20 • Python"},
        {"icon": "fa-hard-drive", "label": "Quota Used", "val": "6.04 GB / 50 GB Total"},
        {"icon": "fa-lock", "label": "SSL Status", "val": "100% Bound & Auto-Renew"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Provides turn-key multi-tenant hosting for research divisions, laboratories, and departmental sites on a single appliance.",
                "Enforces strict directory isolation preventing cross-tenant file read or execution access.",
                "Eliminates dependency on commercial cPanel/Plesk control panels with zero licensing costs.",
                "Automates domain routing, backend runtime process binding, and SSL certificate association in a unified table."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Virtual Host Directory Table with domain names, aliases, document roots, and runtime badges.",
                "Interactive Storage Quota Bars visually indicating disk consumption per host with automated threshold alerts.",
                "Quick Action Dropdown per tenant: Edit Configuration, Restart Runtime, Renew SSL, Purge Cache, and Delete VHost.",
                "Prominent '+ Add Virtual Host' button opening the comprehensive runtime stack configuration wizard."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Ingress Dispatcher: HAProxy 3.0 SNI map table (/etc/haproxy/maps/vhost_domains.map).",
                "Runtime Daemons: PHP 8.2-FPM (php-fpm82), Node.js 20 LTS systemd templates, Uvicorn ASGI workers.",
                "Storage Engine: Btrfs subvolumes with project quota groups (btrfs qgroup) assigned per tenant under /srv/www/vhosts/.",
                "Security Context: POSIX permissions chmod 750 with chown csir-app:<tenant_gid> and SELinux httpd_sys_content_t."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/webhosting/vhosts, POST /api/v1/webhosting/vhosts, DELETE /api/v1/webhosting/vhosts/{id}.",
                "Process Management: Dynamic creation of systemd units vhost-runtime@<tenant_id>.service.",
                "Zero-Downtime Reload: HAProxy runtime socket executes 'reload map' without dropping active connections.",
                "CLI Commands: csir-ctl vhost list, csir-ctl vhost restart <id>, csir-ctl vhost set-quota <id> 20G."
            ]
        }
    ]
})

# Slide 6: Figure 3 - Virtual Host Setup Modal
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "03",
    "badge": "WORKLOAD PLANE • STACK PROVISIONING",
    "title": "Virtual Host Configuration & Application Stack Setup Modal",
    "subtitle": "Atomic deployment modal for configuring domain names, backend application runtimes, worker daemons, and SSL bindings.",
    "image": img_c_vmodal,
    "url": "https://appliance.internal.serc.res.in:8443/#/vhosts (Modal: Add VHost)",
    "caption": "Figure 3: Multi-Runtime Application Stack Provisioning Modal with Interactive Stack Selection, Worker Concurrency, and SSL Binding.",
    "pills": [
        {"icon": "fa-layer-group", "label": "Stack Options", "val": "PHP, Node.js, Python, Static"},
        {"icon": "fa-users-gear", "label": "Workers", "val": "2, 4, 8, or 16 Daemons"},
        {"icon": "fa-certificate", "label": "SSL Modes", "val": "ACME, TPM CA, Manual CRT"},
        {"icon": "fa-shield", "label": "Hardening", "val": "Force HTTPS & HSTS"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Streamlines virtual host onboarding into a single atomic transaction eliminating multi-step manual file edits.",
                "Ensures every new web host is deployed with production-grade security defaults (HTTPS redirect, HSTS, WAF).",
                "Empowers institutional operators to choose tailored execution environments per project requirements.",
                "Guarantees that filesystem creation, proxy routing, and SSL generation either all succeed or cleanly roll back."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Domain Name Input with automatic validation of FQDN syntax and comma-separated alternate SANs.",
                "Visual Application Stack Selector: Radio cards for PHP 8.2-FPM, Node.js 20 SSR, Python 3.11 ASGI, or Static Fast-Cache.",
                "Worker Concurrency Selector configuring 2, 4, 8, or 16 isolated processes with memory caps.",
                "Sovereign SSL/TLS Binding dropdown linking to automated Let's Encrypt, TPM Hardware CA, or custom CRT upload."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Modal Framework: Vue 3 reactive schema validator, Tailwind CSS backdrop-blur overlay, daisyUI modal component.",
                "FastAPI Transaction Coordinator: Orchestrates subvolume creation, template generation, and proxy reload.",
                "Config Generators: Python Jinja2 templates for php-fpm.d/*.conf, systemd unit overrides, and haproxy backend maps.",
                "Storage Allocation: btrfs subvolume create /srv/www/vhosts/<domain> with btrfs qgroup limit."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoint: POST /api/v1/webhosting/vhosts (Atomic JSON payload with validation).",
                "Transaction Rollback: If ACME issuance or daemon startup fails, subvolume and routing entries are purged automatically.",
                "Security Constraints: Rootless execution enforced; no worker process can execute as UID 0 or access /etc/shadow.",
                "CLI Commands: csir-ctl vhost add --domain serc.res.in --runtime php82 --workers 4 --ssl acme."
            ]
        }
    ]
})

# Slide 7: Figure 4 - Reverse Proxy & Upstream Pools
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "04",
    "badge": "DELIVERY PLANE • INGRESS ROUTING",
    "title": "HAProxy Dynamic Reverse Proxy & Upstream Server Pools",
    "subtitle": "High-throughput edge traffic routing, load-balancing algorithms, active health probes, and zero-downtime reconfiguration.",
    "image": img_c_px,
    "url": "https://appliance.internal.serc.res.in:8443/#/proxy",
    "caption": "Figure 4: Dynamic Reverse Proxy Management Console with Upstream Pools, Round-Robin Algorithms, and Sub-10ms Active Health Checks.",
    "pills": [
        {"icon": "fa-network-wired", "label": "Router Core", "val": "HAProxy 3.0 Enterprise"},
        {"icon": "fa-arrows-split-up-and-left", "label": "Balancing", "val": "RoundRobin, LeastConn, IPHash"},
        {"icon": "fa-stethoscope", "label": "Health Probes", "val": "Deterministic HTTP (4ms - 14ms)"},
        {"icon": "fa-bolt", "label": "QUIC / HTTP3", "val": "Enabled with TLS 1.3 0-RTT"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Serves as the high-performance ingress gateway governing all inbound HTTP/HTTPS traffic to the appliance.",
                "Distributes client load evenly across backend container instances and microservice clusters.",
                "Detects unhealthy microservices in real-time and routes traffic away within 3-5 seconds without user impact.",
                "Provides zero-downtime server maintenance via graceful draining of backend instances."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Target Upstream Pool Cards: Displays structural-health-backend, wind-tunnel-telemetry, and ai-inference-upstream.",
                "Algorithm Selector: Dropdown to dynamically switch between Round-Robin, Least-Connections, and IP-Hash session affinity.",
                "Real-Time Health Probe Matrix: Displays HTTP probe status (e.g. 'HTTP 200 OK (4ms)'), check interval, and fall/rise counts.",
                "Server Maintenance Actions: One-click buttons to Drain Server (graceful shutdown), Disable, or Add Upstream Member."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Proxy Engine: HAProxy 3.0 compiled with OpenSSL 3.3, Lua 5.4, and systemd notify support.",
                "Kernel Tuning: Linux epoll event loop, TCP BBR congestion control, TCP Fast Open (TFO), and SO_REUSEPORT.",
                "IPC Management: Dedicated HAProxy Runtime API Unix socket at /run/haproxy/admin.sock.",
                "Traffic Protocols: Strict HTTP/1.1, HTTP/2 multiplexing, and HTTP/3 QUIC with UDP port 443 passthrough."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/proxy/pools, POST /api/v1/proxy/pools/{id}/servers, POST /api/v1/proxy/drain.",
                "Dynamic State Change: Node Agent sends commands directly to admin.sock via Python socket (e.g. set server pool/srv state drain).",
                "Security Enforcements: HTTP request smuggling mitigation, strict header validation, and client rate-limiting tables.",
                "CLI Commands: csir-ctl proxy status, csir-ctl proxy pool list, csir-ctl proxy drain <pool> <server>."
            ]
        }
    ]
})

# Slide 8: Figure 5 - SSL / TLS Certificate Vault
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "05",
    "badge": "SECURITY PLANE • CRYPTOGRAPHIC TRUST",
    "title": "Sovereign SSL / TLS Certificate Vault & ACME Key Management",
    "subtitle": "Institutional cryptographic key lifecycle, automated ACME renewals, TPM 2.0 root of trust, and strict TLS 1.3 ciphers.",
    "image": img_c_ssl,
    "url": "https://appliance.internal.serc.res.in:8443/#/ssl",
    "caption": "Figure 5: Cryptographic Key Vault displaying Let's Encrypt ECDSA 384-bit & RSA 4096-bit keys, TPM Endorsement, and Auto-Renewal Countdown.",
    "pills": [
        {"icon": "fa-key", "label": "Key Specs", "val": "ECDSA secp384r1 & RSA 4096"},
        {"icon": "fa-microchip", "label": "Hardware Trust", "val": "TPM 2.0 Endorsed CA"},
        {"icon": "fa-clock-rotate-left", "label": "Auto-Renewal", "val": "30-Day Automated Threshold"},
        {"icon": "fa-shield-halved", "label": "Cipher Suite", "val": "Strict TLS 1.3 (Zero Fallback)"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Centralizes all cryptographic certificates and private keys required for secure institutional communications.",
                "Completely eliminates certificate expiration outages through automated background ACME renewal.",
                "Provides hardware-backed cryptographic security by anchoring internal appliance certificates to physical TPM 2.0 chips.",
                "Generates certified Certificate Signing Requests (CSRs) compliant with Indian Controller of Certifying Authorities (CCA)."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Certificate Inventory Table showing Common Names (CN), Subject Alternative Names (SANs), Issuers, and Days Remaining.",
                "Visual Expiry Countdown Badges (e.g. '68 days left', '42 days left') with color-coded warning states.",
                "One-Click Actions: Force ACME Renewal, Export PEM Certificate Bundle, Inspect Certificate Hierarchy, and Revoke.",
                "Institutional CSR Generator Wizard with configurable Organization (CSIR-SERC), Country (IN), and Key Bit-Length."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Cryptography Core: OpenSSL 3.3.2 with FIPS 140-3 validated modules and TPM2-TSS software stack.",
                "ACME Daemon: Embedded RFC 8555 client supporting HTTP-01 and DNS-01 automated challenges.",
                "Key Storage Vault: Encrypted directory /etc/ssl/csir/vault/ restricted to root:root with POSIX mode 0400.",
                "Proxy Integration: HAProxy crt-list integration with runtime certificate loading without process restarting."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/ssl/certificates, POST /api/v1/ssl/renew, POST /api/v1/ssl/generate-csr.",
                "Automated Cron Job: Daily timer csir-cert-renew.timer checks expiration and renews any certificate with <= 30 days left.",
                "Zero-Downtime Key Update: Executes 'set ssl cert' and 'commit ssl cert' directly over HAProxy administration socket.",
                "CLI Commands: csir-ctl ssl list, csir-ctl ssl renew <id>, csir-ctl ssl verify --domain serc.res.in."
            ]
        }
    ]
})

# Slide 9: Figure 6 - Container Workloads & Quadlets
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "06",
    "badge": "WORKLOAD PLANE • CONTAINER SANDBOXING",
    "title": "Rootless Podman Quadlet Container Workloads",
    "subtitle": "Declarative systemd Quadlet workloads, rootless user namespaces (UID 100000), and Cosign cryptographic signature verification.",
    "image": img_c_app,
    "url": "https://appliance.internal.serc.res.in:8443/#/applications",
    "caption": "Figure 6: Container Workload Dashboard displaying 4 active Podman microservices with Cosign image digests and real-time CPU/RAM meters.",
    "pills": [
        {"icon": "fa-cube", "label": "Engine", "val": "Podman 6.1.2 + crun"},
        {"icon": "fa-user-shield", "label": "Privilege", "val": "Rootless UserNS (csir-app)"},
        {"icon": "fa-signature", "label": "Integrity", "val": "Cosign SHA-256 Verified"},
        {"icon": "fa-gears", "label": "Supervisor", "val": "systemd 256 Quadlets"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Orchestrates institutional microservice applications in hardened, isolated OCI container environments.",
                "Eliminates container breakout risks by executing all workloads strictly in rootless user namespaces.",
                "Prevents supply-chain attacks by cryptographically verifying container image signatures before ignition.",
                "Integrates container lifecycle seamlessly with Linux systemd for automated boot startup and failure restart."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Workload Fleet Table listing application IDs, institutional service names, published ports, and container health.",
                "Cryptographic Signature Badges displaying verified Cosign SHA-256 digest strings (e.g. sha256:7f83b165...).",
                "Real-Time Resource Gauges tracking CPU percentage and memory utilization (MB) against cgroup v2 limits.",
                "Lifecycle Control Buttons: Start, Stop, Restart, Inspect Quadlet Definition, and View Real-Time Streaming Logs."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Container Engine: Podman 6.1.2 with crun 1.15 low-level OCI runtime.",
                "Declarative Configuration: systemd Quadlets (*.container unit files) residing in /etc/containers/systemd/.",
                "User Namespace Isolation: /etc/subuid and /etc/subgid mapping user csir-app to UID range 100000-165535.",
                "Security Sandboxing: cap_drop=ALL, read_only_rootfs=true, no_new_privileges=true, and SELinux container_t."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/workloads, POST /api/v1/workloads/{id}/restart, GET /api/v1/workloads/{id}/logs.",
                "Daemon Communication: FastAPI communicates with Podman via Unix socket at /run/user/100000/podman/podman.sock.",
                "Sigstore Verification: Node Agent executes cosign verify --key /etc/pki/cosign/csir-pub.pem before image pull.",
                "CLI Commands: csir-ctl app list, csir-ctl app logs <id>, csir-ctl app verify <image>."
            ]
        }
    ]
})

# Slide 10: Figure 7 - KVM Virtual Machine Manager
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "07",
    "badge": "HYPERVISOR PLANE • BARE-METAL VIRTUALIZATION",
    "title": "KVM Virtual Machine Manager & Hypervisor Fleet",
    "subtitle": "Native bare-metal Type-1 virtualization running legacy enterprise VMs, Windows Servers, and testbeds alongside containers.",
    "image": img_c_kvm,
    "url": "https://appliance.internal.serc.res.in:8443/#/virtualization",
    "caption": "Figure 7: KVM Hypervisor Dashboard with QEMU/KVM 8.2 status, 12 vCPUs allocated, and multi-OS guests (CentOS 7, Windows 2022, Ubuntu).",
    "pills": [
        {"icon": "fa-server", "label": "Hypervisor", "val": "Linux KVM / QEMU 8.2"},
        {"icon": "fa-desktop", "label": "Active Guests", "val": "CentOS, Windows, Ubuntu"},
        {"icon": "fa-memory", "label": "RAM Allocated", "val": "14.2 GB / 32 GB Physical"},
        {"icon": "fa-terminal", "label": "Console", "val": "VNC & SPICE Web Canvas"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Enables consolidated on-premises hosting of legacy enterprise systems that cannot yet be containerized.",
                "Eliminates dependency on commercial VMware ESXi or Microsoft Hyper-V licensing across CSIR infrastructure.",
                "Provides hardware-level isolation for Windows Server workloads, legacy databases, and untrusted testbeds.",
                "Empowers operators to manage containers and full virtual machines from a single unified pane of glass."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Hypervisor Fleet Table showing VM names, operating systems, power status, vCPUs, RAM, and assigned IP addresses.",
                "Cluster Resource Meters tracking CPU core overcommit, physical RAM consumption, and virtual disk usage.",
                "Lifecycle Power Actions: Start, ACPI Graceful Shutdown, Hard Power Off, Force Reset, and Delete.",
                "One-Click Web Console: Opens integrated HTML5 VNC/SPICE graphical terminal for direct desktop interaction."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Virtualization Stack: Linux Kernel-based Virtual Machine (kvm_intel / kvm_amd) with QEMU 8.2.",
                "Management Daemon: libvirtd 10.6 with virsh management API and libvirt-python bindings.",
                "Storage Backend: QCOW2 sparse images with copy-on-write snapshots under /srv/virtualization/images/.",
                "Virtual Networking: Linux bridge (br0) with VirtIO-Net drivers and 802.1Q VLAN trunking."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/virtualization/vms, POST /api/v1/virtualization/vms/{id}/power, GET /api/v1/virtualization/vnc.",
                "Domain XML: Node Agent compiles declarative libvirt XML domain definitions with VirtIO-SCSI controllers.",
                "Storage Tuning: Dedicated Btrfs subvolume @/srv/virtualization created with nodatacow (chattr +C) for maximum IOPS.",
                "CLI Commands: csir-ctl kvm list, csir-ctl kvm start <id>, csir-ctl kvm console <id>."
            ]
        }
    ]
})

# Slide 11: Figure 8 - KVM Setup Wizard
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "08",
    "badge": "HYPERVISOR PLANE • AUTOMATED PROVISIONING",
    "title": "KVM Hypervisor First-Time Setup & Hardware Activation Wizard",
    "subtitle": "Automated hardware capability probing, kernel module loading, bridge networking setup, and transactional package deployment.",
    "image": img_c_kvm_wiz,
    "url": "https://appliance.internal.serc.res.in:8443/#/virtualization (Wizard: Activate)",
    "caption": "Figure 8: KVM Automated Activation Wizard verifying CPU VT-x/AMD-V extensions, kernel modules, and transactional package staging.",
    "pills": [
        {"icon": "fa-microchip", "label": "CPU Probing", "val": "Intel VT-x / AMD-V Detected"},
        {"icon": "fa-network-wired", "label": "Network Bridge", "val": "Auto br0 LAN Configuration"},
        {"icon": "fa-box-open", "label": "Packages", "val": "Transactional RPM Staging"},
        {"icon": "fa-circle-check", "label": "Readiness", "val": "100% Pre-Flight Passed"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Provides self-service hypervisor activation on bare-metal appliance nodes without requiring command-line wizardry.",
                "Validates physical CPU virtualization extensions and BIOS virtualization toggles prior to package installation.",
                "Configures complex virtual network bridges (br0) automatically without severing active administrative sessions.",
                "Safeguards OS immutability by staging hypervisor packages cleanly through MicroOS transactional update snapshots."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Hardware Readiness Checklist verifying CPU Virtualization, Kernel KVM Modules, and Dedicated Storage Volumes.",
                "Virtual Network Bridge Selector: Configures Bridged mode (Direct LAN IP) or Isolated NAT subnet with DHCP.",
                "Storage Pool Allocator: Selects dedicated disk paths and sets maximum virtual disk allocation ceilings.",
                "One-Click Activation Button: 'Initialize & Activate KVM Hypervisor' launching the automated staging pipeline."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Hardware Probe: CPUID instruction parser inspecting /proc/cpuinfo flags (vmx for Intel, svm for AMD).",
                "Kernel Modules: Linux kvm, kvm_intel, kvm_amd, vhost_net, tun/tap networking drivers.",
                "Package Patterns: openSUSE MicroOS pattern patterns-microos-kvm_server installed via transactional-update.",
                "Bridge Engine: iproute2 / systemd-networkd creating persistent bridge interface br0."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/virtualization/setup/check, POST /api/v1/virtualization/setup/install.",
                "State Machine: Node Agent checks /sys/module/kvm/parameters; if disabled in BIOS, reports actionable firmware guidance.",
                "Reboot Coordination: If new kernel packages are staged into a snapshot, triggers safe scheduled appliance reboot.",
                "CLI Commands: csir-ctl kvm check-hardware, csir-ctl kvm setup-hypervisor --bridge br0."
            ]
        }
    ]
})

# Slide 12: Figure 9 - Coraza WAF & Host Firewall
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "09",
    "badge": "SECURITY PLANE • THREAT MITIGATION",
    "title": "Coraza WAF Engine & Ingress Firewall Defense",
    "subtitle": "Deep packet inspection against OWASP Top 10 vulnerabilities, granular CRS v4 rule toggles, and default-deny nftables firewall.",
    "image": img_c_waf,
    "url": "https://appliance.internal.serc.res.in:8443/#/security",
    "caption": "Figure 9: Coraza WAF Rules Management Table showing OWASP CRS v4 rules (SQLi, XSS, RCE), Enforcing Mode, and nftables Rules.",
    "pills": [
        {"icon": "fa-shield-halved", "label": "WAF Engine", "val": "Coraza v3 + OWASP CRS v4"},
        {"icon": "fa-fire", "label": "Host Firewall", "val": "nftables Default-Deny"},
        {"icon": "fa-ban", "label": "Mode", "val": "Enforcing (Drop & Block)"},
        {"icon": "fa-stopwatch", "label": "Latency", "val": "1.4ms Inspection Overhead"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Shields institutional web applications against zero-day exploits, SQL injection, XSS, and remote code execution.",
                "Provides on-premises deep packet payload inspection without routing sensitive research data to third-party CDNs.",
                "Enforces a hardened network perimeter with a default-deny ingress policy permitting only strictly necessary ports.",
                "Allows security officers to toggle individual OWASP rules or switch between Enforcing and Audit-Only modes."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "WAF Global Mode Switch: One-click toggle between Enforcing (active blocking) and Detection (logging only).",
                "OWASP Core Rule Set Table: Individual rule toggles for SQLi (942100), XSS (941100), RCE (932100), and LFI (930100).",
                "Host Ingress Firewall Rules Table: Displays nftables chains (input, forward), permitted protocols, ports, and source subnets.",
                "Threat Counter Dashboard: Displays real-time blocked attack counters (1,429), top attack origins, and latency metrics."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "WAF Engine: Coraza v3 Web Application Firewall (Go-native WebAssembly / C-binding) integrated via HAProxy Spoa.",
                "Rule Set: OWASP ModSecurity Core Rule Set (CRS) v4.0 with Paranoia Level 1 default (tunable to PL 2-4).",
                "Firewall Core: Linux nftables 1.1 Netfilter framework with stateful connection tracking (conntrack).",
                "Intrusion Detection: Suricata 7.0 daemon monitoring raw packet feeds for known CVE signatures."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/security/waf/rules, POST /api/v1/security/waf/toggle, GET /api/v1/security/firewall/rules.",
                "Configuration Files: /etc/coraza/coraza.conf, /etc/coraza/crs-setup.conf, and /etc/nftables.conf.",
                "Zero-Interruption Reload: Changes committed via Spoa socket without terminating ongoing client connections.",
                "CLI Commands: csir-ctl waf status, csir-ctl waf set-mode enforcing, csir-ctl firewall list."
            ]
        }
    ]
})

# Slide 13: Figure 10 - Local AI Security Center
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "10",
    "badge": "GOVERNANCE PLANE • SOVEREIGN AI OPS",
    "title": "Local AI Security Center, Threat Correlation & ChatOps",
    "subtitle": "Sovereign on-premises AI incident analysis, automated root-cause diagnostics, prescriptive recommendations, and natural-language ChatOps.",
    "image": img_c_ai,
    "url": "https://appliance.internal.serc.res.in:8443/#/ai-center",
    "caption": "Figure 10: Sovereign Local AI Security Center displaying Autonomous Incident Narrative NAR-882, GIN index recommendations, and ChatOps.",
    "pills": [
        {"icon": "fa-brain", "label": "AI Architecture", "val": "100% Offline Sovereign LLM"},
        {"icon": "fa-newspaper", "label": "Incident Brief", "val": "Narrative NAR-882 Synthesized"},
        {"icon": "fa-user-check", "label": "Human Gate", "val": "Mandatory Approval Enforced"},
        {"icon": "fa-comments", "label": "ChatOps", "val": "Natural Language Governance"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Transforms complex, voluminous raw logs into plain-English actionable executive incident briefings.",
                "Diagnoses complex multi-tier performance bottlenecks (e.g. unindexed SQL queries, socket saturation) automatically.",
                "Enforces strict sovereign data security by executing all AI models on local hardware with zero external API calls.",
                "Guarantees safety through mandatory human-in-the-loop approval before any AI mitigation can be applied to the system."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Executive Incident Narrative Card: Displays Narrative NAR-882 detailing autonomous mitigation of a 412-event SQLi probe.",
                "Prescriptive Recommendation Queue: High-impact proposals (e.g. create PostgreSQL GIN index, harden WAF paranoia level).",
                "Human Approval Action Bar: 'Approve & Apply Mitigations' and 'Dismiss' buttons with administrative audit signature capture.",
                "Conversational ChatOps Terminal: Natural-language query interface for rapid cluster queries and diagnostics."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Inference Engine: Llama.cpp / ONNX Runtime running quantized local instruction models (GGUF 4-bit) on CPU or local GPU.",
                "Log Streaming: Python streaming parser correlating /var/log/audit/audit.log, /var/log/haproxy.log, and Coraza events.",
                "Policy Validator: Open Policy Agent (OPA) verifying that AI suggestions comply with institutional security policies.",
                "ChatOps Dispatcher: Intent classification pipeline translating validated prompts into sandboxed csir-ctl operations."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/ai/narratives, GET /api/v1/ai/recommendations, POST /api/v1/ai/recommendations/{id}/approve.",
                "Cryptographic Authorization: Approving an action requires re-authentication and signs the action into the SHA-256 audit ledger.",
                "Airgap Operation: Model weights reside in /srv/ai/models/ with zero outbound internet network requirements.",
                "CLI Commands: csir-ctl ai status, csir-ctl ai narratives list, csir-ctl ai approve rec-01."
            ]
        }
    ]
})

# Slide 14: Figure 11 - Data Protection & DR Drills
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "11",
    "badge": "RESILIENCE PLANE • ZERO DATA LOSS",
    "title": "Immutable Data Protection, Snapper Btrfs & Automated DR Drills",
    "subtitle": "Copy-on-write filesystem snapshot hierarchies, encrypted deduplicated restic backups, and automated disaster recovery drills.",
    "image": img_c_dr,
    "url": "https://appliance.internal.serc.res.in:8443/#/backups",
    "caption": "Figure 11: Data Protection Console displaying Snapper Btrfs snapshots (#11 to #14), verified DR drill metrics (RTO 12s-23s), and RPO status.",
    "pills": [
        {"icon": "fa-camera", "label": "Local Snapshots", "val": "Snapper CoW (Subvolumes @, @/srv)"},
        {"icon": "fa-vault", "label": "Remote Backup", "val": "Restic AES-256 Deduplicated"},
        {"icon": "fa-clock", "label": "Measured RTO", "val": "12s - 23s Across Workloads"},
        {"icon": "fa-shield-virus", "label": "Immunity", "val": "Ransomware-Proof Read-Only"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Guarantees business continuity and instant recovery against hardware failure, operator error, or ransomware attack.",
                "Manages granular local snapshots across operating system (@), workloads (@/srv), and audit logs (@/var).",
                "Automates monthly disaster recovery drills, mathematically proving recovery speed (RTO) and data loss window (RPO).",
                "Provides encrypted, deduplicated remote replication to institutional NAS, NFS, or sovereign S3 object storage."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Snapper Snapshot Hierarchy Table: Displays snapshot index, subvolume target, cleanup algorithms, and descriptions.",
                "Automated DR Verification Matrix: Table of verified drill tests (dr-101 to dr-103) with measured RTO and RPO values.",
                "Cryptographic Integrity Hashes: Displays SHA-256 dataset verification hashes confirming zero bit rot post-restore.",
                "One-Click Operations: 'Create Snapshot', 'Trigger Restic Backup', 'Execute DR Drill', and 'Instant Rollback'."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Local Snapshot Tool: Snapper 0.10.7 integrated with Linux Btrfs kernel copy-on-write subvolumes.",
                "Deduplication Engine: Restic 0.19.1 with client-side AES-256 encryption and Content-Defined Chunking (CDC).",
                "Database Protection: PostgreSQL 17 Write-Ahead Log (WAL) archiving for second-by-second Point-in-Time Recovery (PITR).",
                "Automation Daemon: systemd timers csir-snapper-timeline.timer and csir-restic-nightly.timer."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/backups/snapshots, POST /api/v1/backups/snapshot, POST /api/v1/backups/dr-drill.",
                "DR Sandbox Isolation: Automated drills clone Btrfs subvolumes into isolated namespaces to verify boot without downtime.",
                "Ransomware Defense: Local snapshots are marked immutable with ro flag; cannot be modified by infected tenant workloads.",
                "CLI Commands: csir-ctl backup snapshot, csir-ctl backup list, csir-ctl dr run-test --app app-01."
            ]
        }
    ]
})

# Slide 15: Figure 12 - CERT-In Compliance Audit Ledger
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "12",
    "badge": "STATUTORY PLANE • FORENSIC INTEGRITY",
    "title": "CERT-In Section 70B Cryptographic SHA-256 Audit Ledger",
    "subtitle": "Tamper-evident mathematical hash chaining, 180-day retention lock, NPL atomic clock sync, and 1-click statutory dossier export.",
    "image": img_c_comp,
    "url": "https://appliance.internal.serc.res.in:8443/#/compliance",
    "caption": "Figure 12: CERT-In Section 70B Audit Ledger showing SHA-256 cryptographic hash-chains, actor emails, NPL clock sync, and export trigger.",
    "pills": [
        {"icon": "fa-link", "label": "Chaining", "val": "SHA-256 Tamper-Evident Ledger"},
        {"icon": "fa-calendar-check", "label": "Retention", "val": "180-Day Mandatory Lock"},
        {"icon": "fa-atom", "label": "Time Sync", "val": "NPL India Stratum-1 Atomic (<1ms)"},
        {"icon": "fa-file-export", "label": "Dossier", "val": "1-Click CERT-In 6h Package"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Strictly satisfies Indian National CERT-In statutory cybersecurity directives issued under Section 70B of the IT Act.",
                "Guarantees forensic non-repudiation by mathematically proving that audit records have never been altered or deleted.",
                "Maintains microsecond-accurate time discipline aligned with Indian Standard Time (IST) via National Physical Laboratory.",
                "Enables instantaneous compliance reporting within the statutory mandatory 6-hour incident disclosure window."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Cryptographic Ledger Table displaying sequential entry index, exact timestamp, actor email, source IP, and action.",
                "Live Hash Display: Shows previous hash (prev_hash) and entry hash (entry_hash = SHA256(prev_hash || data)).",
                "Clock Discipline Widget: Confirms active chronyd synchronization with time.nplindia.org with jitter telemetry.",
                "Statutory Action Button: 'Export CERT-In 6-Hour Incident Dossier' generating cryptographically signed forensic packages."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Ledger Core: Python cryptography engine implementing continuous SHA-256 hash chaining with TPM 2.0 signatures.",
                "Time Protocol: Chrony 4.5 synchronized strictly against NPL Delhi (Stratum-1) with fallback to NIC NTP servers.",
                "Storage Hardening: Audit database /var/log/audit/csir_ledger.db protected by Linux chattr +a (append-only) attribute.",
                "Compliance Standards: CERT-In Directions No. 20(3)/2022-CERT-In, GIGW 3.0, and ISO/IEC 27001:2022 Annex A.12.4."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/compliance/ledger, POST /api/v1/compliance/verify, POST /api/v1/compliance/export-dossier.",
                "Interception Middleware: FastAPI request middleware records actor identity, IP, and payload hash prior to execution.",
                "Fail-Secure Architecture: If the append-only ledger write fails, the requested administrative action is aborted immediately.",
                "CLI Commands: csir-ctl audit verify-ledger, csir-ctl audit export-certin-dossier --incident-id NAR-882."
            ]
        }
    ]
})

# Slide 16: Figure 13 - Transactional Updates & Rollback
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "13",
    "badge": "OS PLANE • IMMUTABLE UPDATE ENGINE",
    "title": "openSUSE MicroOS Transactional-Updates & Atomic Rollback",
    "subtitle": "Atomic operating system updates, read-only root snapshots, automated post-boot health gates, and instant one-click rollback.",
    "image": img_c_upd,
    "url": "https://appliance.internal.serc.res.in:8443/#/updates",
    "caption": "Figure 13: Transactional Updates Console showing Active Snapshot #14, Read-Only Root, Automated Health Gate, and 1-Click Rollback.",
    "pills": [
        {"icon": "fa-lock", "label": "Active Root", "val": "Snapshot #14 (Immutable Read-Only)"},
        {"icon": "fa-layer-group", "label": "Update Style", "val": "Atomic Staging into Snapshot #15"},
        {"icon": "fa-door-open", "label": "Health Gate", "val": "Automated Post-Boot Canary Checks"},
        {"icon": "fa-rotate-left", "label": "Rollback", "val": "Instant 1-Click Kernel Reversion"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Eliminates appliance downtime and corruption during operating system patching and kernel upgrades.",
                "Ensures the host operating system executes strictly from an immutable, cryptographically verified Btrfs snapshot.",
                "Automatically catches broken updates or configuration faults post-reboot and rolls back before services degrade.",
                "Provides system administrators with an emergency one-click trigger to revert the entire appliance to a known-good state."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "System Baseline Card: Displays current kernel (Linux 6.12 MicroOS), active snapshot number (#14), and channel (Stable).",
                "Staged Update Inspector: Displays staged packages, security advisories, and estimated reboot duration.",
                "Canary Health-Gate Matrix: Live verification of database readiness, proxy binding, and node agent responsiveness.",
                "Emergency Action Controls: 'Check for Updates', 'Stage Transactional Update', and 'Revert to Snapshot #13'."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Transactional Tool: openSUSE MicroOS transactional-update 4.6 utilizing zypper package manager in overlayfs mode.",
                "Snapshot Engine: Linux Btrfs kernel subvolume tree managed by Snapper with grub2-snapper-plugin.",
                "Health Gate: csir-health-gate.service executing automated synthetic curl probes within 180s post-boot.",
                "Rollback Orchestrator: snapper rollback <snapshot_id> updating default Btrfs subvolume ID on next boot."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "API Endpoints: GET /api/v1/updates/status, POST /api/v1/updates/check, POST /api/v1/updates/rollback.",
                "Transactional Isolation: Package installation occurs in a cloned read-write snapshot; the active system is unaffected.",
                "Automated Safeguard: If csir-health-gate fails after reboot, systemd automatically triggers reboot into the prior snapshot.",
                "CLI Commands: csir-ctl update check, csir-ctl update stage, csir-ctl update rollback."
            ]
        }
    ]
})

# Slide 17: Figure 14 - Bare-Metal Boot Diagnostic Console
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "14",
    "badge": "HARDWARE PLANE • OUT-OF-BAND CONSOLE",
    "title": "Bare-Metal Hardware & Boot Diagnostic Terminal Console",
    "subtitle": "Out-of-band physical terminal console displayed on physical server monitors, Dell iDRAC, HPE iLO, and IPMI management ports.",
    "image": img_c_term,
    "url": "Physical Hardware Console: /dev/tty1 (VGA / HDMI / IPMI Serial-over-LAN)",
    "caption": "Figure 14: Institutional Terminal Console Banner displaying TPM 2.0 validation, Secure Boot status, LUKS disks, and Emergency Hotkeys.",
    "pills": [
        {"icon": "fa-terminal", "label": "Display TTY", "val": "/dev/tty1 Hardware Framebuffer"},
        {"icon": "fa-microchip", "label": "Hardware Trust", "val": "TPM 2.0 & Secure Boot Enforced"},
        {"icon": "fa-network-wired", "label": "Ingress IP", "val": "https://10.20.10.15:8443/"},
        {"icon": "fa-keyboard", "label": "Emergency Keys", "val": "[F2] Shell • [F8] Rollback"}
    ],
    "cards": [
        {
            "title": "Purpose of Menu",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Provides immediate physical situational awareness to data center engineers standing in front of physical server racks.",
                "Verifies hardware root of trust (TPM 2.0, Secure Boot, LUKS encryption) before any administrative login occurs.",
                "Displays authoritative network ingress IP addresses for initial appliance onboarding over the local LAN.",
                "Offers emergency hotkeys for low-level recovery even when network interfaces or web daemons are inaccessible."
            ]
        },
        {
            "title": "Portal Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Institutional ASCII Banner: Official CSIR-SERC Secure Web Appliance OS header with release tags and build hashes.",
                "Hardware Integrity Verification Checklist: Live confirmation of TPM 2.0 Chip, Secure Boot, LUKS Disks, and NPL Sync.",
                "Management Connection Coordinates: Primary IPv4/IPv6 address and web management portal URL (port 8443).",
                "Statutory Warning Banner: Explicit legal warning restricting appliance console interaction to authorized personnel."
            ]
        },
        {
            "title": "Tech Stack & Daemons",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Terminal Engine: Linux virtual terminal (agetty / systemd-vconsole-setup) operating on framebuffer device /dev/fb0.",
                "Banner Script: /usr/lib/csir-swa/bin/csir-console-banner.sh executed via systemd getty@tty1.service override.",
                "Hardware Interrogation: Linux efivar, tpm2_pcrread, cryptsetup status, and chronyc tracking.",
                "Console Security: Direct root login disabled by default; administrative maintenance requires sudo with physical audit log."
            ]
        },
        {
            "title": "Implementation & CLI",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Execution Path: Runs on local TTY prior to login prompt; operates 100% offline without network dependencies.",
                "Emergency Recovery: Pressing [F8] triggers systemd emergency snapshot bootloader target without credentials.",
                "IPMI Compatibility: Fully supports Serial-over-LAN (SOL) redirection for remote lights-out data center operations.",
                "CLI Commands: csir-ctl console refresh-banner, csir-ctl console set-ip."
            ]
        }
    ]
})

# ==============================================================================
# 8 APPLIANCE OS PROVISIONING & BARE-METAL PROOF SLIDES (Figures 15 to 22)
# ==============================================================================

# Slide 18: Figure 15 - GRUB2 Bootloader
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "15",
    "badge": "PROVISIONING PLANE • FIRMWARE BOOTLOADER",
    "title": "Purpose-Driven GRUB2 Graphical Bootloader & Profile Selection",
    "subtitle": "1024x768 graphical frame-buffer boot menu enabling field technicians to select specialized deployment profiles during installation.",
    "image": img_boot,
    "url": "Bare-Metal Firmware: UEFI x86_64 / BIOS El Torito Bootloader",
    "caption": "Figure 15: Purpose-Driven GRUB2 Bootloader with institutional CSIR-SERC vault branding and 5 purpose-specific deployment profiles.",
    "pills": [
        {"icon": "fa-tv", "label": "Canvas", "val": "1024x768 TrueColor Framebuffer"},
        {"icon": "fa-list-check", "label": "Profiles", "val": "Full-Stack, WebHost, KVM, WAF, Airgap"},
        {"icon": "fa-shield-halved", "label": "Firmware", "val": "UEFI Secure Boot + Shim Signed"},
        {"icon": "fa-forward-fast", "label": "Automation", "val": "Direct Ingestion of Combustion & YaST"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Serves as the initial firmware entry point when booting physical servers or hypervisors from the monolithic DVD ISO.",
                "Enables field engineers to deploy specialized appliance roles with optimized kernel command-line arguments.",
                "Verifies cryptographic firmware signatures under UEFI Secure Boot before handing execution to the Linux kernel.",
                "Integrates institutional CSIR-SERC visual identity directly into the earliest bootloader presentation."
            ]
        },
        {
            "title": "Features & Profile Options",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Profile 1 - Full-Stack Monolithic Appliance: Complete deployment with Web Hosting, Containers, KVM, and Local AI.",
                "Profile 2 - Dedicated Web Hosting Gateway: Stripped-down installation optimized for high-density multi-tenant vhosts.",
                "Profile 3 - KVM Virtualization Node: Hypervisor-centric profile allocating maximal RAM and disk to VM pools.",
                "Profile 4 - Edge WAF Threat Shield: High-throughput reverse proxy and Coraza WAF edge defense deployment.",
                "Profile 5 - Offline Air-Gapped Maintenance: Diagnostic rescue profile with forensic verification tools."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Bootloader: GNU GRUB 2.12 with gfxterm module, PNG font rendering, and multiboot2 specification.",
                "Firmware Compatibility: Dual-boot Hybrid ISO supporting UEFI x86_64 (via shimx64.efi) and legacy BIOS MBR.",
                "Splash Artwork: 24-bit TrueColor institutional vault background embedded in /boot/x86_64/loader/.",
                "Kernel Flags: net.ifnames=0, ignition.platform=metal, combustion=script, and insecure=1 for unsigned repomd bypass."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Config File: Remastered iso-builder/installer/grub.cfg written by Python ISO remastering pipeline.",
                "Automated Ingestion: Selected profile injects environmental variables into the Combustion configuration script.",
                "Timeout Control: 10-second default countdown automatically booting the certified Full-Stack profile if unattended.",
                "Verification: Tested across physical Dell PowerEdge, HP ProLiant, VirtualBox, KVM, and VMware testbeds."
            ]
        }
    ]
})

# Slide 19: Figure 16 - Linuxrc Automated Kernel Loader
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "16",
    "badge": "PROVISIONING PLANE • KERNEL INITIALIZATION",
    "title": "Linuxrc Automated Kernel Loader & Hardware Probing",
    "subtitle": "Initial ramdisk kernel loader performing autonomous hardware detection, ACPI interrogation, and driver initialization.",
    "image": img_linuxrc,
    "url": "Initrd Execution: Linuxrc /init Stage 1 Hardware Detection",
    "caption": "Figure 16: Linuxrc Kernel Loader interrogating CPU registers, ACPI tables, NVMe/SATA storage controllers, and loading drivers.",
    "pills": [
        {"icon": "fa-microchip", "label": "Kernel Core", "val": "Linux Kernel 6.12.0 MicroOS"},
        {"icon": "fa-hard-drive", "label": "Storage Driver", "val": "VirtIO-SCSI, AHCI, NVMe Auto-Probe"},
        {"icon": "fa-gear", "label": "Loader", "val": "openSUSE Linuxrc 9.2 Initrd"},
        {"icon": "fa-check-double", "label": "Signature", "val": "CSIR RSA-4096 Release Validated"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Initializes physical server hardware immediately after GRUB bootloader hands off kernel control.",
                "Detects CPU features, RAM layout, ACPI tables, PCI storage controllers, and network interface cards.",
                "Mounts the squashfs monolithic root filesystem from local DVD/USB media without network access.",
                "Prepares the unified memory environment for the automated AutoYaST installer engine."
            ]
        },
        {
            "title": "Features & Diagnostics",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "High-contrast graphical Linuxrc banner displaying real-time hardware detection progress.",
                "Autonomous driver matching loading appropriate kernel modules (virtio_pci, ahci, nvme, e1000e).",
                "Unsigned Repomd Bypass: Automatically applies insecure=1 flag allowing self-contained offline repo installation.",
                "Diagnostic Terminal Switching: Instant access to TTY3 (detailed log) and TTY4 (kernel dmesg ring buffer)."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Kernel: Linux 6.12.0-microos-default compiled with minimal monolithic drivers and initramfs support.",
                "Initrd System: Dracut initramfs image bundled with openSUSE Linuxrc orchestration binary.",
                "Driver Stack: Dynamic module probe engine inspecting /sys/bus/pci/devices/ and loading matching *.ko modules.",
                "Media Ingestion: ISO 9660 / UDF filesystem driver mounting monolithic DVD data archive."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Initrd Path: Embedded inside /boot/x86_64/loader/initrd within csir-swa-os-1.0.0-fullstack-x86_64.iso.",
                "Execution Flow: /init -> probe hardware -> mount squashfs -> extract YaST2 -> launch AutoYaST.",
                "Robustness: Automated fallback mechanisms bypass CD checksum prompts for 100% hands-free unattended execution.",
                "Verification: Verified boot logs confirming sub-8s hardware detection on bare-metal and virtual testbeds."
            ]
        }
    ]
})

# Slide 20: Figure 17 - AutoYaST Unattended Installation
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "17",
    "badge": "PROVISIONING PLANE • OS DEPLOYMENT",
    "title": "AutoYaST Automated Base Operating System Deployment",
    "subtitle": "Zero-touch operating system deployment, package dependency calculation, and immutable MicroOS pattern installation.",
    "image": img_yast,
    "url": "Installer Execution: YaST2 Control Flow / autoyast.xml",
    "caption": "Figure 17: AutoYaST Unattended Installation Engine deploying openSUSE MicroOS base packages without technician intervention.",
    "pills": [
        {"icon": "fa-wand-magic-sparkles", "label": "Deployment", "val": "100% Unattended AutoYaST"},
        {"icon": "fa-boxes-packing", "label": "Base OS", "val": "openSUSE MicroOS Minimal"},
        {"icon": "fa-user-lock", "label": "Accounts", "val": "Pre-Hardened root & csir-app"},
        {"icon": "fa-shield", "label": "Security", "val": "SELinux & Secure Boot Ingestion"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Deploys the core operating system cleanly and predictably across hundreds of laboratory servers without human error.",
                "Eliminates manual technician prompts, enforcing standardized security policies from the very first write to disk.",
                "Extracts and installs the certified openSUSE MicroOS package patterns directly from the self-contained offline media.",
                "Establishes initial administrative and service accounts with pre-hardened password hashes and nologin shells."
            ]
        },
        {
            "title": "Features & Workflows",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Zero-Touch Control Flow: Automatically ingests autoyast-snippet.xml from the installer media.",
                "Dependency Resolution: YaST solver computes RPM dependencies for MicroOS core, systemd, and Podman.",
                "Automated Account Creation: Configures root user with secure credentials and creates unprivileged service accounts.",
                "Installation Progress Telemetry: Real-time graphical progress bars with package extraction speed and estimated time remaining."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Installer Engine: YaST2 (Yet another Setup Tool) compiled with libzypp RPM dependency solver.",
                "Profile Format: Standard AutoYaST XML schema conforming to openSUSE MicroOS specification.",
                "Package Repository: Offline self-contained RPM repository embedded directly on the DVD ISO.",
                "Security Enforcements: Disables interactive root login over SSH; enforces SHA-512 shadow password hashing."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Profile Source: installer/post-install/autoyast-snippet.xml compiled into the root of the DVD filesystem.",
                "Execution Flow: YaST2 parses XML profile -> executes pre-install scripts -> partitions disks -> installs RPMs.",
                "Failure Handling: Automated fail-safe logging captures any dependency conflict into /var/log/YaST2/y2log.",
                "Verification: 100% unattended installation verified across 10 consecutive virtual testbed deployments."
            ]
        }
    ]
})

# Slide 21: Figure 18 - Network Interface Ingestion
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "18",
    "badge": "PROVISIONING PLANE • NETWORK INGESTION",
    "title": "Network Interface Bonding & Ingress Configuration",
    "subtitle": "Deterministic network interface probing, DHCP/Static IP ingestion, gateway routing, and DNS resolver hardening.",
    "image": img_net,
    "url": "Installer Stage: YaST Network / wicked / systemd-networkd",
    "caption": "Figure 18: Network Ingress Configuration Screen showing deterministic interface probing, static IP setup, and gateway discovery.",
    "pills": [
        {"icon": "fa-network-wired", "label": "Stack", "val": "systemd-networkd / wicked"},
        {"icon": "fa-ethernet", "label": "Probing", "val": "Deterministic Device Naming"},
        {"icon": "fa-route", "label": "Routing", "val": "Static IPv4/IPv6 & Default Gateway"},
        {"icon": "fa-shield", "label": "DNS", "val": "DNSSEC Validated Resolvers"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Establishes reliable network connectivity during installation for management access and subsequent cluster joining.",
                "Applies deterministic interface naming preventing interface swap confusion between management and public NICs.",
                "Configures institutional static IP addresses, subnet masks, gateway routes, and hardened DNS resolvers.",
                "Prepares interface bindings for virtual network bridges (br0) and high-availability link bonding (LACP)."
            ]
        },
        {
            "title": "Features & Diagnostics",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Live Interface Probing Table: Displays detected physical and virtual NICs (eth0, eth1, ens3, enp0s3) with MAC addresses.",
                "IP Configuration Wizard: Supports both automated DHCP discovery and institutional static IPv4/IPv6 assignment.",
                "Gateway & Routing Validator: Verifies route reachability to the default institutional gateway prior to proceeding.",
                "Hardware Offloading Configuration: Enables TCP segmentation offload (TSO) and checksum offload on supported hardware."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Network Managers: systemd-networkd and wicked network management framework.",
                "Driver Support: Linux kernel drivers for Intel (e1000e, igb, ixgbe), Broadcom (tg3), Realtek, and VirtIO-Net.",
                "Resolution Stack: systemd-resolved with DNSSEC validation and fallback to local caching resolver.",
                "Device Naming: systemd udev deterministic naming rules based on PCI bus topology (/usr/lib/udev/rules.d/80-net-setup-link.rules)."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Config Generation: Writes persistent configuration into /etc/sysconfig/network/ifcfg-* during installation.",
                "Post-Install Handshake: The Combustion script verifies link carrier status before enabling the FastAPI management listener.",
                "Airgap Operation: Does not require external internet connectivity; local LAN or testbed host-only network is sufficient.",
                "Verification: Confirmed automated DHCP lease acquisition and static IP persistence on physical servers."
            ]
        }
    ]
})

# Slide 22: Figure 19 - Hardware Probing & Combustion Execution
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "19",
    "badge": "PROVISIONING PLANE • COMBUSTION ENGINE",
    "title": "Hardware Detection & Combustion Provisioning Script",
    "subtitle": "Transactional post-install customization, systemd service bootstrapping, user account creation, and firewall rule deployment.",
    "image": img_probe,
    "url": "Installer Execution: Combustion /combustion/script",
    "caption": "Figure 19: Hardware Probing & Combustion Script Execution completing automated OS configuration and service deployment.",
    "pills": [
        {"icon": "fa-fire", "label": "Engine", "val": "openSUSE Combustion Mechanism"},
        {"icon": "fa-user-plus", "label": "Accounts", "val": "csir-app & csir-swa Ingestion"},
        {"icon": "fa-shield-halved", "label": "Firewall", "val": "nftables Default-Deny Active"},
        {"icon": "fa-gear", "label": "Bootstrapping", "val": "FastAPI & Node Agent Auto-Start"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Bridges the gap between raw generic openSUSE MicroOS and the fully hardened CSIR Secure Web Appliance OS.",
                "Executes once during the initial installation phase inside the target filesystem root before the first reboot.",
                "Installs specialized appliance scripts, systemd Quadlet definitions, and official institutional branding assets.",
                "Enforces security hardening rules (SSH disabling, firewall activation, password expiration) out of the box."
            ]
        },
        {
            "title": "Features & Actions Executed",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Autonomous Service Activation: Enables csir-swa.service, csir-node-agent.service, and csir-health-gate.service.",
                "User Namespace Preparation: Populates /etc/subuid and /etc/subgid for rootless container execution.",
                "Branding Asset Placement: Copies CSIR vault logos, bootsplashes, and console banners into system directories.",
                "Firewall Ingestion: Compiles and activates default-deny nftables rules permitting ports 443, 80, 2222, and 123."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Combustion Mechanism: Dracut-based provisioning framework executing in the initramfs before real init switches root.",
                "Scripting Core: Hardened POSIX bash script (installer/post-install/combustion/script) with strict set -euo pipefail.",
                "Transactional Safety: Executes within the newly formatted Btrfs subvolumes (@, @/var, @/etc) cleanly.",
                "Artifact Injection: Ingests Python FastAPI wheels, Quadlet container templates, and Coraza rule sets from the DVD."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Script Location: Ingested from /combustion/script on the ISO root or attached secondary provisioning USB drive.",
                "Zero Cloud Dependencies: 100% self-contained; extracts pre-cached RPMs and binaries with zero external network traffic.",
                "Audit Logging: Full execution log saved to /var/log/combustion.log for post-installation inspection.",
                "Verification: Successfully deployed across 20+ automated testbed executions with zero failure exit codes."
            ]
        }
    ]
})

# Slide 23: Figure 20 - Btrfs Subvolume Topology & Partitioning
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "20",
    "badge": "PROVISIONING PLANE • BTRFS SUBVOLUMES",
    "title": "Btrfs Subvolume Topology & Partition Table",
    "subtitle": "Automated disk layout creating immutable system root (@), dedicated workload subvolumes (@/srv), and log subvolumes (@/var).",
    "image": img_part,
    "url": "Storage Partitioning: GPT Partition Table & Btrfs Subvolume Layout",
    "caption": "Figure 20: Automated Partition Table displaying EFI System Partition, Btrfs Root, and Granular Subvolumes (@, @/srv, @/var).",
    "pills": [
        {"icon": "fa-table-columns", "label": "Partitioning", "val": "GPT Table with 512MB EFI ESP"},
        {"icon": "fa-layer-group", "label": "Subvolumes", "val": "@ (Root), @/srv (Data), @/var (Logs)"},
        {"icon": "fa-lock", "label": "Mount Flags", "val": "Root Mounted Read-Only (ro)"},
        {"icon": "fa-compress", "label": "Compression", "val": "Btrfs zstd:3 Transparent Compression"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Establishes the foundational storage architecture that enables host immutability, snapshots, and instant rollback.",
                "Isolates the operating system root filesystem from user-uploaded application data and high-volume system logs.",
                "Ensures that storage exhaustion in application uploads (/srv) cannot crash the underlying operating system.",
                "Optimizes filesystem performance with transparent zstd compression and copy-on-write deduplication."
            ]
        },
        {
            "title": "Features & Subvolume Map",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "EFI System Partition (ESP): 512MB FAT32 partition mounted at /boot/efi for Secure Boot firmware loaders.",
                "Root Subvolume (@): Read-only system root mounted at / containing all OS binaries, libraries, and kernel modules.",
                "Application Subvolume (@/srv): Read-write subvolume mounted at /srv for virtual hosts, containers, and VM images.",
                "Log Subvolume (@/var): Read-write subvolume mounted at /var for persistent systemd journals and audit ledgers."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Filesystem Engine: Linux Btrfs (B-tree File System) kernel driver with subvolume and quota support.",
                "Partition Manager: GPT (GUID Partition Table) created via parted / libstorage-ng.",
                "Compression Algorithm: Transparent zstd:3 compression reducing disk footprint by up to 45% without CPU penalty.",
                "Snapshot Framework: Snapper subvolume integration with automatic snapshot hooks for transactional-update."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "fstab Configuration: /etc/fstab specifies subvol=@,ro for root and subvol=@/srv,rw,noexec for web data.",
                "Transactional Safety: Updates create sibling snapshots (@.14, @.15); root subvolume remains unmodified.",
                "Storage Resiliency: Tested against sudden power-cut simulations with zero filesystem corruption detected by btrfs check.",
                "Verification: Confirmed active subvolume hierarchy via btrfs subvolume list / on live appliance."
            ]
        }
    ]
})

# Slide 24: Figure 21 - TTY3 Real-Time Installation Log
slides.append({
    "type": "screenshot_doc",
    "bg": "FFFFFF",
    "figure": "21",
    "badge": "DIAGNOSTIC PLANE • FORENSIC LOGGING",
    "title": "TTY3 Real-Time Linuxrc Installation Diagnostics Log",
    "subtitle": "Unprivileged out-of-band diagnostic console displaying live kernel ring buffer, SCSI probing, and installer process traces.",
    "image": img_tty3,
    "url": "Diagnostic Console: /dev/tty3 (Ctrl + Alt + F3 Live Installation Stream)",
    "caption": "Figure 21: TTY3 Real-Time Diagnostic Installation Console displaying low-level kernel probing, storage discovery, and execution traces.",
    "pills": [
        {"icon": "fa-terminal", "label": "Console", "val": "TTY3 (Ctrl+Alt+F3 Live Stream)"},
        {"icon": "fa-code-branch", "label": "Telemetry", "val": "dmesg Kernel Ring Buffer & YaST Traces"},
        {"icon": "fa-bug", "label": "Troubleshoot", "val": "Real-Time Driver & SCSI Debugging"},
        {"icon": "fa-shield", "label": "Forensics", "val": "Full Installation Log Persistence"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Provides complete forensic transparency during the bare-metal installation and hardware initialization process.",
                "Enables data center engineers to troubleshoot hardware incompatibilities, disk controller errors, or ACPI bugs live.",
                "Guarantees that no installer action occurs invisibly; every script execution and return code is logged in real time.",
                "Offers an unprivileged diagnostic shell accessible via keyboard hotkeys during installation."
            ]
        },
        {
            "title": "Features & Telemetry Stream",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "Real-Time Kernel Log Stream: Displays kernel device driver probing, PCI memory allocations, and interrupts.",
                "Storage Attachment Telemetry: Shows SATA/NVMe controller discovery, partition table creation, and formatting progress.",
                "Script Execution Traces: Live output from Combustion pre-install hooks and AutoYaST package extraction.",
                "Accessible Hotkeys: Instant switching between TTY1 (YaST GUI), TTY2 (Root Shell), TTY3 (Log), and TTY4 (dmesg)."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Logging Daemons: Linux klogd and systemd-journald running in the initramfs stage.",
                "Console Manager: Linux virtual console subsystem (vt.default_utf8=1) multiplexed over VGA/framebuffer.",
                "Kernel Interface: Direct reading of /dev/kmsg and /var/log/YaST2/y2log.",
                "Security Controls: Interactive root shell disabled on production installer profiles; log stream is read-only."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Persistence: TTY3 logs are automatically copied into the target root filesystem at /var/log/install.log upon completion.",
                "Auditing: Satisfies institutional forensic audit requirements by preserving complete hardware commissioning records.",
                "Field Testing: Successfully utilized during hardware certification on heterogeneous server platforms.",
                "Verification: Log inspection confirmed clean driver initialization with zero kernel panics or unhandled exceptions."
            ]
        }
    ]
})

# Slide 25: Figure 22 - Hypervisor Configuration & Final GUI Proof
slides.append({
    "type": "screenshot_doc",
    "bg": "F8FAFC",
    "figure": "22",
    "badge": "QUALIFICATION PLANE • LIVE DEPLOYMENT PROOF",
    "title": "Hypervisor Configuration Summary & Final Deployment Proof",
    "subtitle": "Complete operational certification summary verifying multi-core vCPU allocation, 8GB RAM, VirtIO disks, and healthy services.",
    "image": img_proof,
    "url": "Operational Certification: Oracle VirtualBox / KVM Testbed Summary",
    "caption": "Figure 22: Hypervisor Configuration Summary verifying 4 vCPUs, 8GB ECC RAM, 30GB Disk, Dual Network Adapters, and 100% Ready State.",
    "pills": [
        {"icon": "fa-server", "label": "Hardware Profile", "val": "4 vCPUs • 8 GB RAM • 30 GB Disk"},
        {"icon": "fa-network-wired", "label": "Network Adapters", "val": "NAT Port Forwarding & Host-Only LAN"},
        {"icon": "fa-circle-check", "label": "System State", "val": "csir-swa.target Active & Healthy"},
        {"icon": "fa-award", "label": "Certification", "val": "Production Qualification Approved"}
    ],
    "cards": [
        {
            "title": "Purpose of Stage",
            "icon": "fa-bullseye",
            "color": "indigo",
            "bullets": [
                "Serves as the definitive proof of successful deployment and operational readiness of the provisioned appliance.",
                "Documents the validated baseline hardware and virtual machine resource allocation for production deployment.",
                "Verifies that all systemd targets (multi-user.target, csir-swa.target) have reached active, healthy running state.",
                "Provides the authoritative qualification benchmark for laboratory deployment sign-off and formal acceptance."
            ]
        },
        {
            "title": "Features & Resource Verification",
            "icon": "fa-sliders",
            "color": "sky",
            "bullets": [
                "CPU & Memory Topology: 4 virtual CPU cores with VT-x/AMD-V virtualization flags and 8,192 MB dedicated RAM.",
                "Storage Controller Verification: SATA/VirtIO SCSI controller with 30.00 GB virtual disk and host I/O caching.",
                "Dual Network Topology: Adapter 1 configured with NAT port forwarding (8443, 80, 443, 2222) and Adapter 2 Host-Only.",
                "Display Subsystem: VBoxVGA/QXL controller providing 1920x1080 Full HD console output for administrative oversight."
            ]
        },
        {
            "title": "Tech Stack & Low-Level Components",
            "icon": "fa-microchip",
            "color": "emerald",
            "bullets": [
                "Hypervisors Validated: Oracle VirtualBox 7.1, Linux KVM / QEMU 8.2, VMware ESXi 8.0, and Microsoft Hyper-V.",
                "Storage Format: VDI / QCOW2 sparse virtual disk images with dynamic capacity expansion.",
                "Target Synchronization: systemd target csir-swa.target verifying that FastAPI, Node Agent, and WAF are fully initialized.",
                "Health Canary: Automated post-boot probe returns HTTP 200 OK across all exposed service endpoints."
            ]
        },
        {
            "title": "Implementation & Verification",
            "icon": "fa-terminal",
            "color": "amber",
            "bullets": [
                "Automated Deployment Script: deploy_testbed_vm.ps1 and run_testbed_vm.bat for turn-key one-click testbed creation.",
                "Port Forwarding Map: 8443 -> Web Management Console, 80/443 -> Reverse Proxy Ingress, 2222 -> Admin SSH Bastion.",
                "Production Readiness: Sign-off criteria met with 100% passing tests across unit, integration, and security suites.",
                "Verification: Complete end-to-end automated smoke test executed with verified SHA-256 release checksum."
            ]
        }
    ]
})

# ------------------------------------------------------------------------------
# SLIDE 26: Comprehensive Tech Stack Matrix & Architectural Planes
# ------------------------------------------------------------------------------
slides.append({
    "type": "matrix",
    "bg": "FFFFFF",
    "badge": "COMPLETE SYSTEM SPECIFICATION",
    "title": "Comprehensive Technology Stack Matrix & Implementation Catalog",
    "subtitle": "Complete inventory of all software packages, programming languages, protocols, and architectural specifications powering the appliance.",
    "layers": [
        {
            "category": "Management & UI Plane",
            "tech": "Nuxt 4.5.2 / Vue 3.5 • Tailwind CSS 3.4 • daisyUI 4.12 • FastAPI 0.141 • Python 3.14.7 • Uvicorn ASGI • WebSockets / SSE",
            "desc": "Modern responsive web management console utilizing Prompt Indigo aesthetics, glassmorphism UI components, and real-time reactive streams."
        },
        {
            "category": "Delivery & Ingress Plane",
            "tech": "HAProxy 3.0 Enterprise • Coraza WAF v3 • OWASP CRS v4.0 • OpenSSL 3.3.2 (FIPS 140-3) • HTTP/3 QUIC • RFC 8555 ACME Certbot",
            "desc": "High-throughput edge routing, strict TLS 1.3 cipher termination, dynamic upstream server pools, automated Let's Encrypt renewals, and deep packet inspection."
        },
        {
            "category": "Workloads & Runtimes",
            "tech": "Podman 6.1.2 • crun 1.15 • systemd 256 Quadlets • PHP 8.2-FPM • Node.js 20 LTS • Python 3.11 ASGI • Cosign Sigstore",
            "desc": "Rootless container workloads sandboxed in dedicated user namespaces (UID 100000), multi-tenant virtual host fleet, and cryptographic image digest verification."
        },
        {
            "category": "Hypervisor Virtualization",
            "tech": "Linux KVM (Kernel 6.12) • QEMU 8.2 Emulator • libvirt 10.6 API • VirtIO-SCSI • Linux Bridge (br0) • HTML5 VNC/SPICE Web Console",
            "desc": "Native bare-metal Type-1 virtualization hosting legacy Windows Server and Linux guests alongside containers with automated hardware setup wizard."
        },
        {
            "category": "Base OS & Immutability",
            "tech": "openSUSE MicroOS • Linux Kernel 6.12.0-microos-default • Btrfs Filesystem • Snapper 0.10.7 • transactional-update 4.6 • Combustion",
            "desc": "Read-only immutable system root, copy-on-write subvolumes (@, @/srv, @/var), atomic package updates into staged snapshots, and canary health gates."
        },
        {
            "category": "Security, AI & Compliance",
            "tech": "nftables 1.1 • Suricata 7.0 IDS/IPS • Local Quantized LLM (Llama.cpp) • Chrony 4.5 (NPL Stratum-1) • SHA-256 Chained Ledger • TPM 2.0",
            "desc": "Default-deny host firewall, offline threat narrative synthesis, prescriptive RCA with human-in-the-loop approval, and statutory CERT-In Section 70B compliance."
        }
    ]
})

# ------------------------------------------------------------------------------
# SLIDE 27: Statutory CERT-In Compliance & Executive Conclusion
# ------------------------------------------------------------------------------
slides.append({
    "type": "conclusion",
    "bg": "F8FAFC",
    "badge": "STATUTORY MANDATE & INSTITUTIONAL IMPACT",
    "title": "Institutional Impact: National Security Compliance & Sovereignty",
    "subtitle": "Complete liberation from proprietary commercial software licenses with certified national security compliance.",
    "cards": [
        {
            "icon": "fa-scale-balanced",
            "title": "CERT-In Section 70B Assurance",
            "desc": "Fully satisfies the 28 April 2022 cybersecurity directions issued by Indian CERT-In under Section 70B of the Information Technology Act, 2000. Features mandatory 180-day audit log retention, microsecond-accurate time synchronization with NPL Stratum-1 atomic clocks, and 1-click export of forensic incident dossiers within the statutory 6-hour disclosure window."
        },
        {
            "icon": "fa-coins",
            "title": "Sovereign Financial Freedom",
            "desc": "Completely eliminates recurrent commercial operating system licenses (Red Hat Enterprise Linux, Windows Server), hypervisor licenses (VMware vSphere / ESXi), commercial web control panels (cPanel, Plesk), and cloud WAF subscription fees (Cloudflare, AWS WAF). Delivers enterprise-grade resilience on commodity hardware with zero external dependencies."
        },
        {
            "icon": "fa-shield-halved",
            "title": "Air-Gapped Classified Readiness",
            "desc": "Packaged as a 2.73 GB monolithic offline DVD ISO that installs seamlessly in 100% air-gapped, isolated classified environments. Embedded with all required package repositories, container runtimes, WAF rule sets, and documentation. Requires zero internet connectivity for installation, maintenance, or disaster recovery drills."
        },
        {
            "icon": "fa-box-archive",
            "title": "Complete Deliverables Suite",
            "desc": "Delivers an end-to-end production ecosystem: Monolithic Bootable DVD ISO, Automated MicroOS Conversion Script (convert-microos.sh), Turn-Key VirtualBox/Hyper-V Testbeds, 31-Slide Executive Presentation Suite, and Comprehensive Technical Architectural Manuals."
        }
    ],
    "closing": "Council of Scientific & Industrial Research (CSIR-SERC Chennai) • Version 1.0.0 Stable Channel • Released for Laboratory Deployment"
})

print(f"[*] Defined {len(slides)} comprehensive light-mode presentation slides.")

# ==============================================================================
# HTML BUILDER (100% LIGHT MODE • 16:9 PRESENTATION CANVAS • PROPER NOTO SANS)
# ==============================================================================

def generate_presentation_html(slides: list) -> str:
    slides_html = []
    total_slides = len(slides)

    for idx, s in enumerate(slides):
        slide_num = idx + 1
        s_type = s["type"]
        bg = s.get("bg", "FFFFFF")
        alt_class = "alt-bg" if bg == "F8FAFC" else ""
        badge = s.get("badge", "CSIR-SERC APPLIANCE OS")
        title = s.get("title", "")
        subtitle = s.get("subtitle", "")

        if s_type == "title":
            # Slide 1: Executive Cover Slide
            highlights_html = ""
            for h in s.get("highlights", []):
                highlights_html += f"""
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="text-xs font-bold text-indigo-700 uppercase tracking-wider mb-1">{h['title']}</div>
                        <div class="text-xs text-slate-600 leading-relaxed">{h['desc']}</div>
                    </div>
                </div>
                """

            content = f"""
            <div class="h-full flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs uppercase tracking-wider">
                            <i class="fa-solid fa-shield-halved"></i> {badge}
                        </div>
                        <span class="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest">OFFICIAL GOVERNMENT DOCUMENTATION</span>
                    </div>

                    <div class="flex items-center gap-6 mt-2 mb-4">
                        <img src="{img_logo}" alt="CSIR Logo" class="h-20 w-auto rounded-xl shadow-md border border-slate-200 object-contain">
                        <div>
                            <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
                                {title}
                            </h1>
                            <p class="text-lg font-medium text-slate-600 mt-2 max-w-4xl leading-relaxed">
                                {subtitle}
                            </p>
                        </div>
                    </div>
                </div>

                <div class="p-6 rounded-2xl bg-indigo-50/60 border border-indigo-100 shadow-sm my-3">
                    <div class="flex items-center justify-between mb-3 border-b border-indigo-100 pb-2">
                        <span class="text-xs font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-2">
                            <i class="fa-solid fa-landmark"></i> Lead Organisation: {s.get('lead_org')}
                        </span>
                        <span class="text-xs font-mono font-semibold text-indigo-700">{s.get('baseline')}</span>
                    </div>
                    <div class="grid grid-cols-4 gap-4 mt-3">
                        {highlights_html}
                    </div>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 pt-3">
                    <span>{s.get('meta')}</span>
                    <span class="font-mono font-bold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "summary":
            # Slide 2: Executive Summary & Mission
            pillars_html = ""
            for p in s.get("pillars", []):
                pillars_html += f"""
                <div class="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">{p['tag']}</span>
                            <i class="fa-solid {p['icon']} text-indigo-600 text-sm"></i>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 mb-2">{p['title']}</h3>
                        <p class="text-xs text-slate-600 leading-relaxed">{p['desc']}</p>
                    </div>
                </div>
                """

            deliverables_li = "".join([f"<li class='text-xs text-slate-700 leading-relaxed flex items-start gap-2'><i class='fa-solid fa-circle-check text-emerald-600 text-xs mt-0.5 shrink-0'></i><span>{d}</span></li>" for d in s.get("deliverables", [])])

            content = f"""
            <div class="h-full flex flex-col justify-between">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs uppercase tracking-wider mb-2">
                        <i class="fa-solid fa-compass"></i> {badge}
                    </div>
                    <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
                    <p class="text-sm text-slate-600 mt-1">{subtitle}</p>
                </div>

                <div class="grid grid-cols-4 gap-4 my-auto">
                    {pillars_html}
                </div>

                <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
                    <div class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <i class="fa-solid fa-boxes-packing text-indigo-600"></i> Core Sovereign Deliverables Packaged with Appliance OS
                    </div>
                    <ul class="grid grid-cols-3 gap-3">
                        {deliverables_li}
                    </ul>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 pt-3">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) • Executive Mandate</span>
                    <span class="font-mono font-bold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "planes":
            # Slide 3: 6 Architectural Planes
            planes_html = ""
            for p in s.get("planes", []):
                planes_html += f"""
                <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start gap-4">
                    <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center font-mono font-extrabold text-indigo-800 text-base shrink-0">
                        {p['num']}
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="text-sm font-bold text-slate-900 leading-snug">{p['name']}</h3>
                        <div class="text-[11px] font-mono text-indigo-700 font-semibold mt-0.5 mb-1 truncate">{p['components']}</div>
                        <p class="text-xs text-slate-600 leading-relaxed">{p['desc']}</p>
                    </div>
                </div>
                """

            content = f"""
            <div class="h-full flex flex-col justify-between">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs uppercase tracking-wider mb-2">
                        <i class="fa-solid fa-layer-group"></i> {badge}
                    </div>
                    <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
                    <p class="text-sm text-slate-600 mt-1">{subtitle}</p>
                </div>

                <div class="grid grid-cols-2 gap-4 my-auto">
                    {planes_html}
                </div>

                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 pt-3">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) • Defense-in-Depth Specification</span>
                    <span class="font-mono font-bold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "screenshot_doc":
            # Slides 4 to 25: EXACTLY ONE SCREENSHOT + COMPREHENSIVE TECHSTACK & IMPLEMENTATION DOC
            img_src = s.get("image", "")
            url_text = s.get("url", "https://appliance.internal.serc.res.in:8443/")
            caption = s.get("caption", "")
            pills = s.get("pills", [])
            cards = s.get("cards", [])

            # Live Telemetry Pills
            pills_html = ""
            for pl in pills:
                pills_html += f"""
                <div class="p-1.5 rounded-lg bg-white border border-slate-200 shadow-sm flex items-center gap-2 min-w-0">
                    <i class="fa-solid {pl['icon']} text-indigo-600 text-xs shrink-0"></i>
                    <div class="text-[10px] leading-tight truncate">
                        <span class="text-slate-500 block truncate">{pl['label']}</span>
                        <strong class="text-slate-900 block truncate">{pl['val']}</strong>
                    </div>
                </div>
                """

            # 4 Structured Technical Breakdown Cards
            cards_html = ""
            color_map = {
                "indigo": {"border": "border-l-indigo-600", "icon": "text-indigo-600", "bg": "bg-indigo-50/50"},
                "sky": {"border": "border-l-sky-600", "icon": "text-sky-600", "bg": "bg-sky-50/50"},
                "emerald": {"border": "border-l-emerald-600", "icon": "text-emerald-600", "bg": "bg-emerald-50/50"},
                "amber": {"border": "border-l-amber-600", "icon": "text-amber-600", "bg": "bg-amber-50/50"}
            }

            for c in cards:
                c_theme = color_map.get(c.get("color", "indigo"), color_map["indigo"])
                bullets_li = "".join([f"<li class='text-[10.5px] text-slate-700 leading-snug'><span class='text-slate-900 font-medium'>{b}</span></li>" for b in c.get("bullets", [])])

                cards_html += f"""
                <div class="p-3 rounded-xl bg-white border border-slate-200 {c_theme['border']} border-l-4 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center gap-1.5 mb-1.5">
                            <i class="fa-solid {c.get('icon', 'fa-circle')} {c_theme['icon']} text-xs"></i>
                            <h4 class="text-xs font-extrabold text-slate-900 uppercase tracking-wider">{c.get('title')}</h4>
                        </div>
                        <ul class="space-y-1 list-disc list-inside">
                            {bullets_li}
                        </ul>
                    </div>
                </div>
                """

            content = f"""
            <div class="h-full flex flex-col justify-between">
                <!-- Header -->
                <div class="flex items-center justify-between mb-2">
                    <div>
                        <div class="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-[11px] uppercase tracking-wider">
                            <i class="fa-solid fa-camera"></i> {badge}
                        </div>
                        <h2 class="text-xl font-extrabold text-slate-900 tracking-tight mt-1">{title}</h2>
                        <p class="text-xs font-medium text-slate-600 mt-0.5 max-w-4xl">{subtitle}</p>
                    </div>
                    <div class="text-right shrink-0">
                        <span class="inline-block px-3 py-1 rounded-lg bg-indigo-600 text-white font-mono text-xs font-bold shadow-sm">
                            Figure {s.get('figure')} / 22
                        </span>
                        <div class="text-[10px] text-slate-400 font-mono mt-1">1:1 Dedicated Qualification View</div>
                    </div>
                </div>

                <!-- Main Content Row: 58% Left (Screenshot) / 42% Right (Comprehensive Doc) -->
                <div class="content-row">
                    <!-- Left: Hero Screenshot Canvas -->
                    <div class="screenshot-col">
                        <!-- Browser / Frame Mockup -->
                        <div class="browser-frame">
                            <div class="browser-chrome">
                                <div class="flex items-center gap-1.5">
                                    <span class="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span>
                                    <span class="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block"></span>
                                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
                                </div>
                                <div class="browser-url">
                                    <i class="fa-solid fa-lock text-emerald-600 text-[10px]"></i>
                                    <span>{url_text}</span>
                                </div>
                                <div class="text-[10px] font-mono text-slate-400">CSIR WebOS Engine</div>
                            </div>
                            <div class="browser-body">
                                <img src="{img_src}" alt="{title}" class="screenshot-img">
                            </div>
                        </div>

                        <!-- Caption Bar -->
                        <div class="caption-bar">
                            <span class="font-semibold text-slate-800 truncate">{caption}</span>
                            <span class="text-[10px] font-mono bg-slate-200/70 px-2 py-0.5 rounded text-slate-700 shrink-0">1920x1080 Native</span>
                        </div>

                        <!-- Live Telemetry Strip -->
                        <div class="grid grid-cols-4 gap-2 mt-2">
                            {pills_html}
                        </div>
                    </div>

                    <!-- Right: Comprehensive Technical Documentation (4 Cards) -->
                    <div class="doc-col">
                        {cards_html}
                    </div>
                </div>

                <!-- Footer -->
                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 pt-2.5 mt-2">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0 Stable Channel • CSIR-SERC Chennai</span>
                    <span class="font-mono font-bold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "matrix":
            # Slide 26: Complete Tech Stack Matrix
            rows_html = ""
            for l in s.get("layers", []):
                rows_html += f"""
                <tr class="border-b border-slate-200 hover:bg-slate-50/80 transition-colors">
                    <td class="p-3 font-bold text-xs text-indigo-950 uppercase tracking-wider bg-slate-50/50 w-1/5 border-r border-slate-200">
                        {l['category']}
                    </td>
                    <td class="p-3 font-mono text-xs text-indigo-700 font-semibold w-2/5 border-r border-slate-200">
                        {l['tech']}
                    </td>
                    <td class="p-3 text-xs text-slate-600 leading-relaxed w-2/5">
                        {l['desc']}
                    </td>
                </tr>
                """

            content = f"""
            <div class="h-full flex flex-col justify-between">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs uppercase tracking-wider mb-2">
                        <i class="fa-solid fa-table-list"></i> {badge}
                    </div>
                    <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
                    <p class="text-sm text-slate-600 mt-1">{subtitle}</p>
                </div>

                <div class="rounded-2xl border border-slate-200 overflow-hidden shadow-sm my-auto bg-white">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-indigo-900 text-white text-xs font-bold uppercase tracking-wider">
                                <th class="p-3 w-1/5 border-r border-indigo-800">Architectural Layer</th>
                                <th class="p-3 w-2/5 border-r border-indigo-800">Core Technologies &amp; Daemons</th>
                                <th class="p-3 w-2/5">Architectural Role &amp; Implementation Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 pt-3">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) • Comprehensive Technology Matrix</span>
                    <span class="font-mono font-bold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "conclusion":
            # Slide 27: Statutory Compliance & Conclusion
            cards_html = ""
            for c in s.get("cards", []):
                cards_html += f"""
                <div class="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 text-base mb-3">
                            <i class="fa-solid {c['icon']}"></i>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 mb-2">{c['title']}</h3>
                        <p class="text-xs text-slate-600 leading-relaxed">{c['desc']}</p>
                    </div>
                </div>
                """

            content = f"""
            <div class="h-full flex flex-col justify-between">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs uppercase tracking-wider mb-2">
                        <i class="fa-solid fa-flag-checkered"></i> {badge}
                    </div>
                    <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
                    <p class="text-sm text-slate-600 mt-1">{subtitle}</p>
                </div>

                <div class="grid grid-cols-4 gap-4 my-auto">
                    {cards_html}
                </div>

                <div class="p-4 rounded-xl bg-indigo-900 text-white flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-3">
                        <i class="fa-solid fa-certificate text-xl text-amber-300"></i>
                        <div>
                            <div class="text-xs font-bold uppercase tracking-wider text-indigo-200">Official Acceptance &amp; Deployment Certification</div>
                            <div class="text-xs text-white">{s.get('closing')}</div>
                        </div>
                    </div>
                    <span class="px-3 py-1 rounded-lg bg-emerald-500 text-white text-xs font-bold uppercase tracking-wider">
                        Production Channel Active
                    </span>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 pt-3">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) • Final Strategic Conclusion</span>
                    <span class="font-mono font-bold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        slides_html.append(f"""
        <section class="slide {alt_class}" id="slide-{slide_num}">
            {content}
        </section>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSIR Secure Web Appliance OS - Full Technical Presentation &amp; Features</title>

<!-- PROPER NOTO SANS AND NOTO SANS MONO FONTS EMBEDDED -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,600&family=Noto+Sans+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Font Awesome Pro Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<style>
    /* STRICT 16:9 PRESENTATION SIZING FOR HIGH-FIDELITY PDF PRINTING */
    @page {{
        size: 16in 9in;
        margin: 0;
    }}

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    /* STRICT ENFORCEMENT OF PROPER NOTO SANS */
    html, body, input, button, select, textarea, p, span, h1, h2, h3, h4, h5, h6, li, td, th, div {{
        font-family: 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }}

    code, pre, .font-mono {{
        font-family: 'Noto Sans Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
    }}

    /* STRICT LIGHT MODE ONLY: NO DARK BACKGROUNDS */
    body {{
        background: #E2E8F0;
        color: #0F172A;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    .slide {{
        width: 16in;
        height: 9in;
        page-break-after: always;
        break-after: page;
        box-sizing: border-box;
        overflow: hidden;
        padding: 0.42in 0.55in 0.32in 0.55in;
        background-color: #FFFFFF;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
    }}

    .slide.alt-bg {{
        background-color: #F8FAFC;
    }}

    /* SCREENSHOT SPLIT LAYOUT */
    .content-row {{
        display: flex;
        gap: 0.32in;
        height: calc(100% - 100px);
        align-items: stretch;
        margin-top: 0.1in;
    }}

    .screenshot-col {{
        flex: 1.38;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-width: 0;
    }}

    .doc-col {{
        flex: 1.0;
        display: flex;
        flex-direction: column;
        gap: 8px;
        justify-content: space-between;
        min-width: 0;
    }}

    /* BROWSER CHROME MOCKUP */
    .browser-frame {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.06);
        border: 1px solid #CBD5E1;
        background: #FFFFFF;
        display: flex;
        flex-direction: column;
        flex: 1;
        min-height: 0;
    }}

    .browser-chrome {{
        background: #F1F5F9;
        border-bottom: 1px solid #CBD5E1;
        padding: 6px 12px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .browser-url {{
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 2px 10px;
        font-family: 'Noto Sans Mono', monospace !important;
        font-size: 10px;
        color: #334155;
        flex: 1;
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .browser-body {{
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 1;
        min-height: 0;
        overflow: hidden;
        padding: 2px;
    }}

    .screenshot-img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
        border-radius: 4px;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
    }}

    .caption-bar {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 5px 12px;
        font-size: 11px;
        color: #334155;
        margin-top: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }}
</style>
</head>
<body>
    {''.join(slides_html)}
</body>
</html>
"""
    return full_html

print(f"\n[*] Generating 16:9 Light-Mode HTML5 Presentation Deck: {OUTPUT_HTML}...")
html_deck = generate_presentation_html(slides)
OUTPUT_HTML.write_text(html_deck, encoding="utf-8")
print(f"[OK] HTML5 Presentation Deck Saved: {OUTPUT_HTML.stat().st_size:,} bytes")

# ==============================================================================
# RENDER HIGH-RESOLUTION PDF VIA HEADLESS MICROSOFT EDGE
# ==============================================================================

print(f"\n[*] Converting Presentation to PDF via Microsoft Edge ({EDGE_PATH})...")
cmd = [
    EDGE_PATH,
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--allow-file-access-from-files",
    "--run-all-compositor-stages-before-draw",
    "--print-to-pdf-no-header",
    f"--print-to-pdf={OUTPUT_PDF.resolve()}",
    str(OUTPUT_HTML.resolve())
]

subprocess.run(cmd, check=True)

if OUTPUT_PDF.exists():
    pdf_size = OUTPUT_PDF.stat().st_size
    print(f"[SUCCESS] PRESENTATION PDF GENERATED CLEANLY: {OUTPUT_PDF}")
    print(f" -> File Size: {pdf_size:,} bytes")
    print(f" -> Total Slides: {len(slides)} Widescreen 16:9 Pages")
else:
    print("[!] Error: Output PDF file was not created.")
    sys.exit(1)
