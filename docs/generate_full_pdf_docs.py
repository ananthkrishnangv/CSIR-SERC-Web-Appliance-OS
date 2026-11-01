#!/usr/bin/env python3
"""
CSIR Secure Web Appliance OS (CSIR-SWA OS)
Full Technical Documentation & Architectural Specification PDF Generator
Compiles comprehensive project manual, architectural planes, script catalog,
and high-resolution screenshot gallery into an executive-grade PDF.
"""

import os
import sys
import html
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
OUTPUT_HTML = DOCS_DIR / "CSIR-SWA-OS-Complete-Documentation.html"
OUTPUT_PDF = DOCS_DIR / "CSIR-SWA-OS-Complete-Documentation.pdf"

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def read_code(rel_path: str, max_lines: int = 150) -> str:
    full_path = BASE_DIR / rel_path
    if not full_path.exists():
        return f"# File {rel_path} not found"
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            if len(lines) > max_lines:
                raw = "".join(lines[:max_lines]) + f"\n... [Truncated for readability: {len(lines) - max_lines} more lines] ..."
            else:
                raw = "".join(lines)
            return html.escape(raw)
    except Exception as e:
        return f"# Error reading {rel_path}: {e}"

def generate_html() -> str:
    print("[*] Reading source code files for script catalog...")
    code_install_sh = read_code("installer/install.sh", 120)
    code_convert_microos = read_code("installer/convert-microos.sh", 140)
    code_setup_appliance = read_code("installer/setup-appliance.sh", 110)
    code_combustion = read_code("installer/post-install/combustion/script", 50)
    code_firstboot_service = read_code("installer/post-install/csir-firstboot.service", 50)
    code_cloud_init = read_code("installer/post-install/cloud-init/user-data.yaml", 50)
    code_autoyast = read_code("installer/post-install/autoyast-snippet.xml", 50)
    code_health_gate = read_code("appliance-os/kiwi/root/usr/lib/csir-swa/bin/csir-health-gate.sh", 90)
    code_dr_drill = read_code("installer/modules/09_backups_dr.sh", 100)
    code_node_agent = read_code("backend/node_agent/agent.py", 110)
    code_csir_ctl = read_code("backend/cli/csir_ctl.py", 100)
    code_kiwi_config = read_code("appliance-os/kiwi/config.xml", 100)

    # Relative paths from docs/
    logo_src = "../installer/assets/branding/csir-webos-logo.jpg"
    splash_src = "../installer/assets/branding/csir-webos-bootsplash.jpg"
    boot_menu_src = "screenshots/installer/vm_boot_menu_v2.jpg"
    yast_init_src = "screenshots/installer/vm_step4_yast.jpg"
    yast_net_src = "screenshots/installer/vm_step5_yast_net.jpg"
    probing_src = "screenshots/installer/vm_step7_probing_done.jpg"
    partitioning_src = "screenshots/installer/vm_step8_partitioning.jpg"
    final_proof_src = "screenshots/installer/vm_final_gui_proof_ready2.jpg"
    tty3_src = "screenshots/installer/vm_tty3_log.jpg"
    linuxrc_src = "screenshots/installer/vm_installer_linuxrc.jpg"

    console_ov_src = "screenshots/web_console/web_console_01_overview.png"
    console_vh_src = "screenshots/web_console/web_console_02_vhosts.png"
    console_vmodal_src = "screenshots/web_console/web_console_02b_vhost_modal.png"
    console_px_src = "screenshots/web_console/web_console_03_proxy.png"
    console_ssl_src = "screenshots/web_console/web_console_04_ssl.png"
    console_app_src = "screenshots/web_console/web_console_05_applications.png"
    console_kvm_src = "screenshots/web_console/web_console_06_virtualization_kvm.png"
    console_kvm_wiz_src = "screenshots/web_console/web_console_06b_kvm_setup_wizard.png"
    console_waf_src = "screenshots/web_console/web_console_07_security_waf.png"
    console_ai_src = "screenshots/web_console/web_console_08_ai_security_center.png"
    console_dr_src = "screenshots/web_console/web_console_09_data_protection_backups.png"
    console_comp_src = "screenshots/web_console/web_console_10_compliance_audit_ledger.png"
    console_upd_src = "screenshots/web_console/web_console_11_transactional_updates.png"
    console_boot_src = "screenshots/web_console/web_console_12_boot_screen_console.png"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CSIR Secure Web Appliance OS (CSIR-SWA OS) - Technical Documentation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    @page {{
        size: A4;
        margin: 16mm 14mm 16mm 14mm;
    }}

    body {{
        font-family: 'Noto Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 9.5pt;
        line-height: 1.5;
        color: #1e293b;
        margin: 0;
        padding: 0;
        background: #ffffff;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Montserrat', sans-serif;
        letter-spacing: -0.02em;
    }}

    .cover-page {{
        page-break-after: always;
        min-height: 90vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 10px 0;
    }}

    .cover-header {{
        border-bottom: 4px solid #003366;
        padding-bottom: 20px;
    }}

    .cover-logo {{
        max-width: 280px;
        height: auto;
        margin-bottom: 15px;
    }}

    .cover-title {{
        font-size: 24pt;
        font-weight: 800;
        color: #312e81;
        margin: 0 0 8px 0;
        line-height: 1.15;
        text-transform: uppercase;
        letter-spacing: -0.5px;
    }}

    .cover-subtitle {{
        font-size: 12pt;
        font-weight: 500;
        color: #6366f1;
        margin: 0 0 12px 0;
    }}

    .cover-badge {{
        display: inline-block;
        padding: 5px 12px;
        background: #f5f3ff;
        color: #312e81;
        font-weight: 700;
        font-size: 8.5pt;
        border-radius: 4px;
        border: 1px solid #ddd6fe;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .cover-meta-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        background: #f5f3ff;
        border: 1px solid #ddd6fe;
        border-left: 4px solid #6366f1;
        padding: 16px;
        border-radius: 6px;
        margin: 20px 0;
    }}

    .meta-item {{
        font-size: 8.5pt;
    }}

    .meta-label {{
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        font-size: 7pt;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }}

    .meta-value {{
        font-weight: 600;
        color: #0f172a;
    }}

    .cover-footer {{
        border-top: 1px solid #e2e8f0;
        padding-top: 12px;
        font-size: 8pt;
        color: #64748b;
        line-height: 1.4;
    }}

    .page-break {{
        page-break-after: always;
    }}

    h1, h2, h3, h4 {{
        color: #1e1b4b;
        font-weight: 700;
        page-break-after: avoid;
    }}

    h1 {{
        font-size: 16pt;
        border-bottom: 2px solid #312e81;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 12px;
        color: #312e81;
    }}

    h2 {{
        font-size: 12.5pt;
        border-bottom: 1px solid #ddd6fe;
        padding-bottom: 4px;
        margin-top: 16px;
        margin-bottom: 8px;
        color: #1e1b4b;
    }}

    h3 {{
        font-size: 10.5pt;
        margin-top: 12px;
        margin-bottom: 5px;
        color: #4338ca;
    }}

    p {{
        margin-top: 0;
        margin-bottom: 8px;
        text-align: justify;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 8pt;
        page-break-inside: avoid;
    }}

    th, td {{
        border: 1px solid #ddd6fe;
        padding: 5px 8px;
        text-align: left;
        vertical-align: top;
    }}

    th {{
        background-color: #312e81;
        color: #ffffff;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 7.5pt;
        letter-spacing: 0.3px;
    }}

    tr:nth-child(even) td {{
        background-color: #f5f3ff;
    }}

    .callout {{
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
        font-size: 8.5pt;
        page-break-inside: avoid;
    }}

    .callout-info {{
        background: #f5f3ff;
        border-left: 4px solid #6366f1;
    }}

    .callout-warn {{
        background: #fffbeb;
        border-left: 4px solid #d97706;
    }}

    .callout-title {{
        font-weight: 700;
        margin-bottom: 3px;
        color: #0f172a;
    }}

    pre, code {{
        font-family: "Cascadia Code", "Fira Code", Consolas, Menlo, Monaco, monospace;
    }}

    code {{
        background-color: #f1f5f9;
        padding: 1px 3px;
        border-radius: 3px;
        font-size: 8pt;
        color: #0f172a;
    }}

    pre {{
        background: #0b1526;
        color: #e2e8f0;
        padding: 10px 12px;
        border-radius: 4px;
        font-size: 7.5pt;
        line-height: 1.35;
        overflow-x: hidden;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 8px 0;
        page-break-inside: avoid;
        border: 1px solid #1e293b;
    }}

    .script-box {{
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        margin: 12px 0;
        overflow: hidden;
        page-break-inside: avoid;
    }}

    .script-header {{
        background: #1e293b;
        color: #f8fafc;
        padding: 6px 10px;
        font-weight: 600;
        font-size: 8pt;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .script-body pre {{
        margin: 0;
        border-radius: 0;
        border: none;
        max-height: 440px;
    }}

    .screenshot-figure {{
        margin: 10px 0;
        page-break-inside: avoid;
        text-align: center;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        background: #f8fafc;
        padding: 8px;
    }}

    .screenshot-figure img {{
        max-width: 95%;
        height: auto;
        border-radius: 6px;
        border: 1px solid #ddd6fe;
        box-shadow: 0 4px 12px rgba(49, 46, 129, 0.08);
    }}

    .caption {{
        font-size: 8pt;
        font-weight: 600;
        color: #312e81;
        margin-top: 6px;
        text-align: center;
    }}

    .arch-diagram {{
        background: #1e1b4b;
        color: #a78bfa;
        font-family: monospace;
        padding: 10px;
        border-radius: 4px;
        font-size: 7pt;
        line-height: 1.2;
        margin: 8px 0;
        white-space: pre;
        page-break-inside: avoid;
        border: 1px solid #312e81;
    }}

    .grid-2 {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <img src="{logo_src}" class="cover-logo" alt="CSIR-SERC Logo">
        <div class="cover-title">CSIR SECURE WEB APPLIANCE OS</div>
        <div class="cover-subtitle">Complete Technical Specification, Architectural Blueprints, Universal Conversion Engine &amp; Operational Verification Manual</div>
        <div class="cover-badge">Version 1.0.0 • Production Stable Channel • openSUSE MicroOS Baseline</div>
    </div>

    <div class="cover-meta-grid">
        <div class="meta-item">
            <div class="meta-label">Lead Institution</div>
            <div class="meta-value">CSIR-SERC (Structural Engineering Research Centre), Chennai</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Participating Laboratories</div>
            <div class="meta-value">Council of Scientific &amp; Industrial Research (All 37 National Labs)</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Distribution Format</div>
            <div class="meta-value">Monolithic Offline DVD (2.73 GB) &amp; Universal Online Bootstrap</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Underlying Base OS</div>
            <div class="meta-value">openSUSE MicroOS (Immutable Btrfs + Snapper Snapshots)</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Compliance Mandates</div>
            <div class="meta-value">CERT-In 180-Day Log Retention &amp; 6h Dossier, GIGW, ISO 27001</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Document Reference</div>
            <div class="meta-value">CSIR-SWA-DOC-2026-V1.0-PRODUCTION</div>
        </div>
    </div>

    <div class="screenshot-figure" style="padding:4px; margin:0;">
        <img src="{splash_src}" style="max-height:160px; width:auto;" alt="CSIR Bootsplash">
        <div class="caption">Official Institutional Bootsplash &amp; Visual Identity (CSIR-SERC Secure Platform)</div>
    </div>

    <div class="cover-footer">
        <strong>Notice:</strong> This official document specifies the engineering architecture, security controls, installation scripts, and post-installation automation workflows for CSIR Secure Web Appliance OS (CSIR-SWA OS). Intended for System Administrators, DevOps Engineers, and Information Security Officers across CSIR research centres.
    </div>
</div>

<!-- CHAPTER 1: OVERVIEW & ARCHITECTURE -->
<div class="page-break"></div>
<h1>1. Executive Overview &amp; Architectural Planes</h1>

<p>
<strong>CSIR Secure Web Appliance OS (CSIR-SWA OS)</strong> is an immutable, hardened, transactionally updated appliance operating system engineered specifically to host, shield, monitor, and recover institutional web portals, laboratory mini-sites, scientific dashboards, APIs, and containerized microservices across CSIR institutions.
</p>

<h2>1.1 The Six Isolated Architectural Planes</h2>
<p>
The platform strictly decouples duties and access privileges into six discrete operational planes:
</p>

<div class="arch-diagram">[External Clients / Public Internet Traffic]
                  │
                  ▼ (Ports 80, 443)
┌────────────────────────────────────────────────────────┐
│ 1. Web Delivery &amp; Edge Security Plane                  │
│    • nftables default-deny host firewall               │
│    • HAProxy 3.0 reverse proxy with TLS 1.3 enforcement│
│    • Coraza WAF with OWASP Core Rule Set (CRS) v4      │
│    • Suricata 7.0 network IDS/IPS telemetry sensor     │
└──────────────────────────┬─────────────────────────────┘
                           │ Proxied Socket (127.0.0.1)
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Application &amp; Workload Plane                        │
│    • Rootless Podman 6.1.2 with systemd Quadlets       │
│    • Dedicated user namespaces (csir-app:100000:65536) │
│    • Read-only container root &amp; cap_drop=ALL           │
│    • Pre-certified templates (Research Portal, API)    │
└────────────┬─────────────────────────────┬─────────────┘
             │                             │
             ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ 3. Immutable Base OS      │ │ 4. Management Plane       │
│    • openSUSE MicroOS core│ │    • UX4G Nuxt 4 / Vue 3  │
│    • Btrfs read-only root │ │    • FastAPI Control Plane│
│    • transactional-update │ │    • Privileged Node Agent│
│    • Health-gate rollbacks│ │    • OPA Policy Engine    │
└────────────┬──────────────┘ └────────────┬──────────────┘
             │                             │
             ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ 5. Data Protection Plane  │ │ 6. Local AI &amp; Governance  │
│    • Btrfs Snapper snaps  │ │    • Local AI Sec Center  │
│    • Restic deduplication │ │    • Threat Correlation   │
│    • PostgreSQL 17 PITR   │ │    • Hash-chained ledger  │
│    • Automated DR drills  │ │    • CERT-In 6h dossier   │
└───────────────────────────┘ └───────────────────────────┘</div>

<h2>1.2 Plane Descriptions</h2>
<table>
    <tr>
        <th style="width:25%;">Architectural Plane</th>
        <th style="width:35%;">Core Technologies</th>
        <th style="width:40%;">Institutional Security Boundary</th>
    </tr>
    <tr>
        <td><strong>1. Web Delivery &amp; Edge Security</strong></td>
        <td>nftables 1.1, HAProxy 3.0, Coraza WAF v3, OWASP CRS v4, Suricata 7.0</td>
        <td>Enforces default-deny packet filtering, TLS 1.3 termination, OWASP Top 10 web exploit mitigation, and ingress anomaly inspection.</td>
    </tr>
    <tr>
        <td><strong>2. Workload &amp; Container Plane</strong></td>
        <td>Podman 6.1.2, systemd Quadlets, crun, Netavark, Aardvark DNS</td>
        <td>Runs unprivileged containers under dedicated UID namespace (<code>csir-app:100000</code>) with read-only root filesystems and all Linux capabilities dropped.</td>
    </tr>
    <tr>
        <td><strong>3. Immutable Base OS</strong></td>
        <td>openSUSE MicroOS kernel 6.12, Btrfs subvolumes, Snapper, transactional-update</td>
        <td>Mounts <code>/</code> read-only. Updates are executed as atomic Btrfs transactions activated on staged reboot with health-gate verification.</td>
    </tr>
    <tr>
        <td><strong>4. Management &amp; Control Plane</strong></td>
        <td>Nuxt 4 / Vue 3 (UX4G Design), FastAPI Python backend, Node Agent RPC</td>
        <td>Strictly prohibits arbitrary shell injection. Privileged OS actions require typed, allowlisted RPC messages dispatched over <code>/run/csir-swa/agent.sock</code>.</td>
    </tr>
    <tr>
        <td><strong>5. Data Protection &amp; DR Plane</strong></td>
        <td>Snapper timeline snapshots, Restic encrypted deduplication, PostgreSQL 17</td>
        <td>Hourly and daily timeline Btrfs snapshots, AES-256 encrypted offsite backup repo, and automated sandbox disaster recovery drill validation.</td>
    </tr>
    <tr>
        <td><strong>6. Local AI &amp; Governance Plane</strong></td>
        <td>Local AI Threat Engine, SHA-256 Hash-Chain Audit Ledger, NPL India NTP</td>
        <td>Zero external cloud leakage. In-memory threat correlation, 180-day audit retention, 6-hour CERT-In incident dossier export, and atomic clock time sync.</td>
    </tr>
</table>

<h2>1.3 Interface Topology &amp; Service Port Matrix</h2>
<table>
    <tr>
        <th>Port</th>
        <th>Protocol</th>
        <th>Bound IP</th>
        <th>Service Name</th>
        <th>Purpose &amp; Access Scope</th>
    </tr>
    <tr>
        <td><strong>8443</strong></td>
        <td>TCP (HTTPS)</td>
        <td>0.0.0.0</td>
        <td>UX4G Management Portal</td>
        <td>Web UI Administration Console (TLS 1.3, MFA TOTP enforced)</td>
    </tr>
    <tr>
        <td><strong>8000</strong></td>
        <td>TCP (HTTP)</td>
        <td>127.0.0.1</td>
        <td>FastAPI Control Plane</td>
        <td>REST API backend, Swagger documentation at <code>/docs</code></td>
    </tr>
    <tr>
        <td><strong>80</strong></td>
        <td>TCP (HTTP)</td>
        <td>0.0.0.0</td>
        <td>Edge Reverse Proxy</td>
        <td>Plain HTTP ingress (automatically redirects with 301 to HTTPS 443)</td>
    </tr>
    <tr>
        <td><strong>443</strong></td>
        <td>TCP (HTTPS)</td>
        <td>0.0.0.0</td>
        <td>Coraza WAF + HAProxy</td>
        <td>Hardened public ingress for hosted research portals &amp; APIs</td>
    </tr>
    <tr>
        <td><strong>5432</strong></td>
        <td>TCP</td>
        <td>127.0.0.1</td>
        <td>PostgreSQL 17</td>
        <td>Internal relational store (SCRAM-SHA-256 authenticated)</td>
    </tr>
    <tr>
        <td><strong>6432</strong></td>
        <td>TCP</td>
        <td>127.0.0.1</td>
        <td>PgBouncer</td>
        <td>High-concurrency database connection pooling</td>
    </tr>
    <tr>
        <td><strong>9090</strong></td>
        <td>TCP</td>
        <td>127.0.0.1</td>
        <td>Prometheus</td>
        <td>Metrics scraper for node exporter and Podman cgroups</td>
    </tr>
    <tr>
        <td><strong>3000</strong></td>
        <td>TCP (HTTP)</td>
        <td>127.0.0.1</td>
        <td>Grafana Dashboard</td>
        <td>Visual operational telemetry and health dashboards</td>
    </tr>
    <tr>
        <td><strong>Unix Sock</strong></td>
        <td>Local IPC</td>
        <td>/run/csir-swa/agent.sock</td>
        <td>Privileged Node Agent</td>
        <td>Secure typed RPC boundary with CAP_SYS_ADMIN bounding set</td>
    </tr>
</table>

<h2>1.5 Native Web Hosting, Virtual Hosts, Reverse Proxy &amp; SSL Key Vault</h2>
<p>
Beyond containerized microservices, CSIR-SWA OS incorporates an enterprise sovereign web hosting engine designed to host classified laboratory portals, public research websites, and high-throughput sensor endpoints directly:
</p>
<ul>
    <li><strong>Multi-Tenant Virtual Host Isolation:</strong> Segregated document roots under <code>/srv/www/vhosts/&lt;domain&gt;/</code> with distinct user ownership, storage quotas, and bandwidth limits.</li>
    <li><strong>Multi-Runtime Worker Pools:</strong> Native process managers supporting PHP 8.2-FPM pools, Node.js 20 Server-Side Rendering (SSR), Python ASGI (FastAPI/Uvicorn), and static asset caching engines.</li>
    <li><strong>HAProxy Dynamic Reverse Proxy:</strong> Layer 7 traffic routing with upstream target pools, load-balancing algorithms (Round-Robin, Least Connections, IP-Hash), and active health check probes.</li>
    <li><strong>Automated SSL/TLS Key Vault:</strong> ACME Let's Encrypt integration for automatic certificate issuance and renewal, institutional wildcard key vaults, in-browser CSR generation, and TLS 1.3 strict cipher configuration with OCSP stapling.</li>
</ul>

<!-- CHAPTER 2: DEPLOYMENT MODALITIES -->
<div class="page-break"></div>
<h1>2. Installation Modalities &amp; Platform Deployment</h1>

<p>
CSIR-SWA OS supports four deployment pathways to adapt to air-gapped data centers, cloud infrastructure, and existing Linux installations:
</p>

<h2>2.1 Modality Comparison Matrix</h2>
<table>
    <tr>
        <th>Modality</th>
        <th>Target Environment</th>
        <th>Delivery Vehicle</th>
        <th>Internet Required</th>
        <th>Key Advantage</th>
    </tr>
    <tr>
        <td><strong>Method 1: Monolithic DVD ISO</strong></td>
        <td>Bare-metal servers, new hypervisor VMs</td>
        <td><code>csir-swa-os-1.0.0-fullstack-x86_64.iso</code> (2.73 GB)</td>
        <td>No (100% Offline)</td>
        <td>Self-contained DVD containing all packages, YaST graphical installer, and offline repository.</td>
    </tr>
    <tr>
        <td><strong>Method 2: Universal Online Bootstrap</strong></td>
        <td>Existing physical servers, cloud VMs</td>
        <td><code>installer/install.sh</code> via curl | sudo bash</td>
        <td>Yes (HTTPS)</td>
        <td>Zero git dependency; stream-unpacks tarball and auto-routes based on OS detection.</td>
    </tr>
    <tr>
        <td><strong>Method 3: Dedicated MicroOS Converter</strong></td>
        <td>Running openSUSE MicroOS / Leap Micro</td>
        <td><code>installer/convert-microos.sh</code></td>
        <td>Yes</td>
        <td>Atomic <code>transactional-update</code> staging into a fresh Btrfs snapshot; maintains immutability.</td>
    </tr>
    <tr>
        <td><strong>Method 4: Universal Appliance Wizard</strong></td>
        <td>openSUSE Leap, Rocky, AlmaLinux, Fedora</td>
        <td><code>installer/setup-appliance.sh</code></td>
        <td>Yes / Offline Tarball</td>
        <td>Interactive or unattended multi-profile converter with legacy conflict cleanup.</td>
    </tr>
</table>

<h2>2.2 Method 1: Monolithic Full-Stack Offline DVD ISO</h2>
<p>
The bootable monolithic DVD ISO (2.73 GB) is compiled via <code>remaster-full-dvd.py</code>. It contains the complete RPM payload, custom YaST easy installer graphics, bootsplash, and Combustion automation hooks.
</p>
<pre># Command to build the Monolithic Full-Stack DVD ISO:
python -u iso-builder/remaster-full-dvd.py

# Boot Menu Options on DVD:
1. Install CSIR Secure Web Appliance OS (GUI Easy Installer) [Default]
2. Install CSIR Secure Web Appliance OS (Automated Express Installation via AutoYaST)
3. Install CSIR-SWA OS (Hardened Strategic Air-Gapped Mode)
4. CSIR Rescue &amp; Recovery System (Btrfs Snapshot Maintenance)</pre>

<h2>2.3 Method 2: Universal Online Remote Bootstrap</h2>
<p>
A resilient one-liner launcher that requires no pre-installed <code>git</code> or development tools. It streams the archive directly through <code>curl</code> / <code>tar</code>, detects terminal piping, and launches the appropriate engine:
</p>
<pre># 1. Interactive Conversion (Terminal-Aware):
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash

# 2. Unattended Full-Stack Installation with Automated Reboot:
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash -s -- --unattended --all --reboot

# 3. Dedicated Profile (e.g. Edge WAF Reverse Proxy only):
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash -s -- --profile edge-waf --reboot

# 4. Injected via Environment Variables (Cloud-Init friendly):
export CSIR_PROFILE="full" CSIR_UNATTENDED="true" CSIR_REBOOT="true"
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo -E bash</pre>

<h2>2.4 Method 3: Dedicated openSUSE MicroOS Transactional Converter</h2>
<p>
Unlike standard Linux systems, openSUSE MicroOS mounts the root filesystem read-only. Direct <code>zypper install</code> fails at runtime. The dedicated script <code>convert-microos.sh</code> bundles all packages into a <strong>single atomic transaction</strong>:
</p>
<pre># Run on any vanilla openSUSE MicroOS server:
sudo ./installer/convert-microos.sh --unattended --all --reboot</pre>

<!-- CHAPTER 3: POST-INSTALLATION AUTOMATION -->
<div class="page-break"></div>
<h1>3. Post-Installation Automation (After OS Installation Over)</h1>

<p>
In production data centers and cloud deployments, servers are typically provisioned via base OS images, PXE kickstarts, or hypervisor templates. Once the operating system installation finishes, automated post-installation hooks transform the node into a CSIR Secure Web Appliance without manual intervention.
</p>

<h2>3.1 In-Depth Analysis of the Five Post-Install Mechanisms</h2>
<table>
    <tr>
        <th>Mechanism</th>
        <th>Lifecycle Execution Timing</th>
        <th>Immutability Safe</th>
        <th>Configuration File</th>
        <th>Primary Use Case</th>
    </tr>
    <tr>
        <td><strong>1. Combustion Hook</strong></td>
        <td>Initramfs phase during the very first boot of the machine</td>
        <td><strong>100% Native</strong></td>
        <td><code>installer/post-install/combustion/script</code></td>
        <td>Bare-metal MicroOS servers, USB provisioning drives, QEMU <code>fw_cfg</code>.</td>
    </tr>
    <tr>
        <td><strong>2. Systemd First-Boot Unit</strong></td>
        <td>First boot after network-online.target is established</td>
        <td><strong>100% Native</strong></td>
        <td><code>installer/post-install/csir-firstboot.service</code></td>
        <td>Golden VM templates (VMware, VirtualBox, KVM), pre-baked images.</td>
    </tr>
    <tr>
        <td><strong>3. Cloud-Init (User-Data)</strong></td>
        <td>First boot during <code>cloud-final</code> service</td>
        <td><strong>100% Native</strong></td>
        <td><code>installer/post-install/cloud-init/user-data.yaml</code></td>
        <td>Cloud infrastructure (OpenStack, Proxmox NoCloud, AWS, Azure, NIC Cloud).</td>
    </tr>
    <tr>
        <td><strong>4. AutoYaST Post-Script</strong></td>
        <td>End of YaST installer before initial reboot (in <code>/mnt</code>)</td>
        <td>Requires chroot handling</td>
        <td><code>installer/post-install/autoyast-snippet.xml</code></td>
        <td>Automated YaST unattended DVD / PXE mass network installations.</td>
    </tr>
    <tr>
        <td><strong>5. Remote SSH Bootstrap</strong></td>
        <td>After OS reboots and administrator authenticates</td>
        <td><strong>100% Native</strong></td>
        <td>Remote command line</td>
        <td>Ad-hoc conversions, existing servers, testing and laboratory setups.</td>
    </tr>
</table>

<h2>3.2 Mechanism Details &amp; Sample Implementation</h2>

<h3>A. Combustion Automation (Recommended for openSUSE MicroOS)</h3>
<p>
Combustion runs in the initramfs before userspace loads. It mounts persistent disks, configures network routes, and triggers the online bootstrap launcher:
</p>
<pre>#!/bin/bash
# combustion: network
set -euxo pipefail
# Fetch and run the online bootstrap unattended
curl -sSL --retry 5 https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | bash -s -- --unattended --all
exit 0</pre>

<h3>B. Systemd First-Boot Unit (`csir-firstboot.service`)</h3>
<p>
Placed into <code>/etc/systemd/system/csir-firstboot.service</code>. It checks for the absence of the receipt file and triggers once the network is verified online:
</p>
<pre>[Unit]
Description=CSIR-SERC Secure Web Appliance OS Post-Install Firstboot Provisioner
After=network-online.target
Wants=network-online.target
ConditionPathExists=!/etc/csir-swa/installation-receipt.json

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c "curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | bash -s -- --unattended --all --reboot"

[Install]
WantedBy=multi-user.target</pre>

<h2>3.3 Transactional Boot Health Gate &amp; Automatic Rollback</h2>
<p>
When <code>convert-microos.sh</code> stages packages into a new Btrfs root snapshot, the system updates <code>/etc/transactional-update.conf</code> to execute <code>csir-health-gate.sh</code> on next boot.
</p>

<div class="callout callout-info">
    <div class="callout-title">Automated Rollback Guarantee</div>
    If any service (Node Agent, Control Plane REST API, HAProxy, nftables, or Audit Ledger) fails the health gate check upon booting into the new snapshot, <code>snapper rollback</code> automatically activates and the server reboots back into the clean baseline snapshot. This guarantees 100% crash-proof deployment.
</div>

<!-- CHAPTER 4: VISUAL SCREENSHOTS GALLERY -->
<div class="page-break"></div>
<h1>4. Visual Proof &amp; Verification Screenshot Gallery</h1>

<p>
The following high-resolution screenshots document the live installation, bootloader branding, partitioning, and diagnostic consoles captured during virtual machine and bare-metal qualification tests:
</p>

<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{boot_menu_src}" alt="Boot Menu V2">
        <div class="caption">Figure 4.1: Official CSIR-SERC High-Resolution GRUB2 Bootloader Menu with Graphical Easy Installer and Automated Express Installation Entries</div>
    </div>
    <div class="screenshot-figure">
        <img src="{yast_init_src}" alt="YaST Initialization">
        <div class="caption">Figure 4.2: Graphical YaST Installer Engine Initialization &amp; Combustion Hooks</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{yast_net_src}" alt="Network Discovery">
        <div class="caption">Figure 4.3: Automated Network Interface Discovery &amp; Static/DHCP Addressing</div>
    </div>
    <div class="screenshot-figure">
        <img src="{probing_src}" alt="Hardware Probing">
        <div class="caption">Figure 4.4: System Hardware Probing &amp; Storage Controller Identification</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{partitioning_src}" alt="Btrfs Subvolume Layout">
        <div class="caption">Figure 4.5: Immutable Btrfs Subvolume Partitioning Scheme (@, @/var, @/srv)</div>
    </div>
    <div class="screenshot-figure">
        <img src="{final_proof_src}" alt="Final Confirmation">
        <div class="caption">Figure 4.6: YaST Final Automated Installation Confirmation with Full CSIR Feature Payload</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{tty3_src}" alt="TTY3 Diagnostic Shell">
        <div class="caption">Figure 4.7: TTY3 Real-Time Linuxrc Installation Log &amp; Storage Mounting</div>
    </div>
    <div class="screenshot-figure">
        <img src="{linuxrc_src}" alt="Linuxrc Console">
        <div class="caption">Figure 4.8: Linuxrc Text-Mode Fallback Console for Low-Memory (&le; 2048 MB) Nodes</div>
    </div>
</div>

<h2>4.2 UX4G Web Management Console Live Verification</h2>
<p>
The following screenshots demonstrate the operational status and user experience of the UX4G Web Management Console running on the deployed CSIR-SWA OS appliance:
</p>

<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_ov_src}" alt="Overview Dashboard">
        <div class="caption">Figure 4.9: UX4G Executive Dashboard - Central Health Score (98.4%), Workloads &amp; Real-Time Telemetry</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_vh_src}" alt="Web Hosting & Virtual Hosts">
        <div class="caption">Figure 4.10: Native Web Hosting &amp; Multi-Tenant Virtual Host Fleet (PHP/Node/Static &amp; Storage Quotas)</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_vmodal_src}" alt="Add Virtual Host Modal">
        <div class="caption">Figure 4.11: Virtual Host Configuration Modal - Background Stack (PHP/Node/Python/Static) &amp; Automated SSL Setup</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_px_src}" alt="Reverse Proxy & Upstreams">
        <div class="caption">Figure 4.12: Dynamic Reverse Proxy &amp; Upstream Load Balancer (HAProxy Pools, Routes &amp; Health Probes)</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_ssl_src}" alt="SSL / TLS Key Vault">
        <div class="caption">Figure 4.13: Sovereign SSL/TLS Certificate Vault &amp; Key Management (ACME Auto-Renew &amp; TLS 1.3 Strict)</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_app_src}" alt="Applications Quadlets">
        <div class="caption">Figure 4.14: Rootless Podman Quadlet Workloads - Cosign Digest Verification &amp; UserNS Isolation</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_kvm_src}" alt="KVM Virtual Machine Manager">
        <div class="caption">Figure 4.15: KVM Virtual Machine Manager - Active Hypervisor, VT-x/AMD-V Acceleration &amp; Guest VM Fleet</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_kvm_wiz_src}" alt="KVM Setup Wizard">
        <div class="caption">Figure 4.16: KVM Subsystem Setup &amp; Installation Wizard - One-Click Transactional Virtualization Deployment</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_waf_src}" alt="Coraza WAF">
        <div class="caption">Figure 4.17: Coraza WAF &amp; nftables Telemetry - OWASP CRS Rules, Active Deny Policies &amp; Blocked Probes</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_ai_src}" alt="Local AI Security Center">
        <div class="caption">Figure 4.18: Local AI Security &amp; Operations Center - Autonomous Threat Briefings &amp; Human Governance Gate</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_dr_src}" alt="Data Protection & DR">
        <div class="caption">Figure 4.19: Data Protection &amp; Snapshots - Snapper Btrfs Trees, Restic Encryption &amp; DR Sandbox Drills</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_comp_src}" alt="CERT-In Audit Ledger">
        <div class="caption">Figure 4.20: CERT-In Compliance Ledger - Append-Only SHA-256 Hash Chain &amp; 180-Day Retention Lock</div>
    </div>
</div>

<div class="page-break"></div>
<div class="grid-2">
    <div class="screenshot-figure">
        <img src="{console_upd_src}" alt="Transactional Updates">
        <div class="caption">Figure 4.21: Transactional Updates Lifecycle - Read-Only Root Snapshots &amp; Health-Gated Auto-Rollback</div>
    </div>
    <div class="screenshot-figure">
        <img src="{console_boot_src}" alt="Hardware Console Banner">
        <div class="caption">Figure 4.22: Bare-Metal Hardware &amp; Diagnostic Terminal Console Banner (Section 6 Specification)</div>
    </div>
</div>

<!-- CHAPTER 5: COMPLETE SCRIPT & SOURCE CATALOG -->
<div class="page-break"></div>
<h1>5. Comprehensive Script &amp; Codebase Catalog</h1>

<p>
This section provides complete technical documentation, input parameters, execution contexts, and source listings for all key scripts across the CSIR-SWA OS repository:
</p>

<h2>5.1 Universal Remote Bootstrap Launcher (`installer/install.sh`)</h2>
<p>
<strong>Location:</strong> <code>installer/install.sh</code> | <strong>Permissions:</strong> 0755 | <strong>Execution Context:</strong> Remote Root (curl | sudo bash)
</p>
<div class="script-box">
    <div class="script-header">
        <span>installer/install.sh</span>
        <span>Online Bootstrap Engine</span>
    </div>
    <div class="script-body">
        <pre>{code_install_sh}</pre>
    </div>
</div>

<div class="page-break"></div>
<h2>5.2 Dedicated openSUSE MicroOS Converter (`installer/convert-microos.sh`)</h2>
<p>
<strong>Location:</strong> <code>installer/convert-microos.sh</code> | <strong>Permissions:</strong> 0755 | <strong>Execution Context:</strong> Local Root on openSUSE MicroOS
</p>
<div class="script-box">
    <div class="script-header">
        <span>installer/convert-microos.sh</span>
        <span>MicroOS Transactional Engine</span>
    </div>
    <div class="script-body">
        <pre>{code_convert_microos}</pre>
    </div>
</div>

<div class="page-break"></div>
<h2>5.3 Universal Interactive Appliance Wizard (`installer/setup-appliance.sh`)</h2>
<p>
<strong>Location:</strong> <code>installer/setup-appliance.sh</code> | <strong>Permissions:</strong> 0755 | <strong>Execution Context:</strong> Local Root on Standard Linux
</p>
<div class="script-box">
    <div class="script-header">
        <span>installer/setup-appliance.sh</span>
        <span>Universal Conversion Wizard</span>
    </div>
    <div class="script-body">
        <pre>{code_setup_appliance}</pre>
    </div>
</div>

<div class="page-break"></div>
<h2>5.4 Post-Installation Automation Hooks (`installer/post-install/`)</h2>

<h3>A. Combustion Script (`installer/post-install/combustion/script`)</h3>
<div class="script-box">
    <div class="script-header">
        <span>installer/post-install/combustion/script</span>
        <span>Combustion First-Boot Hook</span>
    </div>
    <div class="script-body">
        <pre>{code_combustion}</pre>
    </div>
</div>

<h3>B. Systemd First-Boot Unit (`installer/post-install/csir-firstboot.service`)</h3>
<div class="script-box">
    <div class="script-header">
        <span>installer/post-install/csir-firstboot.service</span>
        <span>Systemd Oneshot Firstboot</span>
    </div>
    <div class="script-body">
        <pre>{code_firstboot_service}</pre>
    </div>
</div>

<h3>C. Cloud-Init User-Data (`installer/post-install/cloud-init/user-data.yaml`)</h3>
<div class="script-box">
    <div class="script-header">
        <span>installer/post-install/cloud-init/user-data.yaml</span>
        <span>Cloud-Init User Data</span>
    </div>
    <div class="script-body">
        <pre>{code_cloud_init}</pre>
    </div>
</div>

<h3>D. AutoYaST Snippet (`installer/post-install/autoyast-snippet.xml`)</h3>
<div class="script-box">
    <div class="script-header">
        <span>installer/post-install/autoyast-snippet.xml</span>
        <span>AutoYaST Post-Script Block</span>
    </div>
    <div class="script-body">
        <pre>{code_autoyast}</pre>
    </div>
</div>

<div class="page-break"></div>
<h2>5.5 Boot Health Gate Verification (`csir-health-gate.sh`)</h2>
<p>
<strong>Location:</strong> <code>appliance-os/kiwi/root/usr/lib/csir-swa/bin/csir-health-gate.sh</code> | <strong>Execution Context:</strong> Systemd boot check
</p>
<div class="script-box">
    <div class="script-header">
        <span>appliance-os/kiwi/root/usr/lib/csir-swa/bin/csir-health-gate.sh</span>
        <span>Boot Health Gate</span>
    </div>
    <div class="script-body">
        <pre>{code_health_gate}</pre>
    </div>
</div>

<h2>5.6 Privileged Node Agent Daemon (`backend/node_agent/agent.py`)</h2>
<p>
<strong>Location:</strong> <code>backend/node_agent/agent.py</code> | <strong>Execution Context:</strong> Root Daemon over Unix Socket
</p>
<div class="script-box">
    <div class="script-header">
        <span>backend/node_agent/agent.py</span>
        <span>Node Agent Allowlist RPC</span>
    </div>
    <div class="script-body">
        <pre>{code_node_agent}</pre>
    </div>
</div>

<div class="page-break"></div>
<h2>5.7 Appliance Administration CLI (`backend/cli/csir_ctl.py`)</h2>
<p>
<strong>Location:</strong> <code>backend/cli/csir_ctl.py</code> (Symlinked to <code>/usr/local/bin/csir-ctl</code>)
</p>
<div class="script-box">
    <div class="script-header">
        <span>backend/cli/csir_ctl.py</span>
        <span>Unified CLI Tool</span>
    </div>
    <div class="script-body">
        <pre>{code_csir_ctl}</pre>
    </div>
</div>

<h2>5.8 KIWI NG 9 Description Schema (`appliance-os/kiwi/config.xml`)</h2>
<p>
<strong>Location:</strong> <code>appliance-os/kiwi/config.xml</code> | <strong>Execution Context:</strong> KIWI NG OEM Image Builder
</p>
<div class="script-box">
    <div class="script-header">
        <span>appliance-os/kiwi/config.xml</span>
        <span>KIWI NG Appliance XML</span>
    </div>
    <div class="script-body">
        <pre>{code_kiwi_config}</pre>
    </div>
</div>

<!-- CHAPTER 6: CREDENTIALS & OPERATIONS -->
<div class="page-break"></div>
<h1>6. Default Credentials, Port Matrix &amp; Operations</h1>

<h2>6.1 Web Portal &amp; Administrative Accounts</h2>
<p>
Access Management Portal via HTTPS: <code>https://&lt;APPLIANCE_IP&gt;:8443/</code>
</p>
<table>
    <tr>
        <th>Account Role</th>
        <th>Username</th>
        <th>Default Password</th>
        <th>Default TOTP</th>
        <th>Permissions Scope</th>
    </tr>
    <tr>
        <td><strong>Super Administrator</strong></td>
        <td><code>admin</code></td>
        <td><code>CsirWebOS@2026!</code></td>
        <td><code>123456</code></td>
        <td>Full appliance administration, updates, container deployment, rollback.</td>
    </tr>
    <tr>
        <td><strong>Security Officer</strong></td>
        <td><code>sec-officer</code></td>
        <td><code>SecOfficer@2026!</code></td>
        <td><code>123456</code></td>
        <td>WAF management, CERT-In dossier export, audit ledger verification.</td>
    </tr>
    <tr>
        <td><strong>Operations Operator</strong></td>
        <td><code>operator</code></td>
        <td><code>Operator@2026!</code></td>
        <td><code>123456</code></td>
        <td>App deployment, service restarts, backup trigger, telemetry dashboards.</td>
    </tr>
    <tr>
        <td><strong>Audit Inspector</strong></td>
        <td><code>auditor</code></td>
        <td><code>Auditor@2026!</code></td>
        <td><code>123456</code></td>
        <td>Read-only cryptographic log verification, compliance inspections.</td>
    </tr>
</table>

<h2>6.2 System &amp; Database Credentials</h2>
<table>
    <tr>
        <th>Account / Service</th>
        <th>UID:GID</th>
        <th>Default Credential / Secret</th>
        <th>Storage / Binding Location</th>
    </tr>
    <tr>
        <td><strong>OS Root</strong></td>
        <td>0:0</td>
        <td><code>CsirRoot@2026!</code> (Console Only)</td>
        <td>Linux Shadow / Console tty1 only (SSH disabled by default)</td>
    </tr>
    <tr>
        <td><strong>csir-swa</strong></td>
        <td>998:998</td>
        <td>No interactive password</td>
        <td>FastAPI daemon user in <code>/var/lib/csir-swa</code></td>
    </tr>
    <tr>
        <td><strong>csir-app</strong></td>
        <td>100000:65536</td>
        <td>No interactive password</td>
        <td>Rootless Podman isolation account in <code>/etc/subuid</code></td>
    </tr>
    <tr>
        <td><strong>PostgreSQL DB App</strong></td>
        <td>csir_admin</td>
        <td><code>CsirPgSecure@2026!</code></td>
        <td>SCRAM-SHA-256 on 127.0.0.1:5432 (<code>csir_swa_db</code>)</td>
    </tr>
    <tr>
        <td><strong>JWT Secret Key</strong></td>
        <td>System Token</td>
        <td>Auto-generated 32-char hex</td>
        <td><code>/etc/csir-swa/control-plane.env</code> (chmod 600)</td>
    </tr>
    <tr>
        <td><strong>Restic Backup Key</strong></td>
        <td>AES-256 Key</td>
        <td><code>CsirResticBackup@2026!</code></td>
        <td><code>/etc/csir-swa/backup-keys/restic.key</code></td>
    </tr>
</table>

<h2>6.3 Unified Appliance CLI (`csir-ctl`) Command Reference</h2>
<pre># Check overall appliance status, release channel, and health status:
csir-ctl status

# List all hosted Quadlet container applications:
csir-ctl apps list

# Deploy a certified research portal container:
csir-ctl apps deploy --name "Institutional Portal" --image "docker.io/library/nginx:alpine" --port 8080

# Verify the cryptographic SHA-256 hash-chain audit ledger:
csir-ctl audit verify

# Export an official CERT-In formatted cyber incident reporting dossier:
csir-ctl audit cert-in

# Execute an automated sandbox disaster recovery restore drill:
csir-ctl backup dr-drill

# Stage a signed transactional update:
csir-ctl updates stage --channel Stable</pre>

<!-- CHAPTER 7: COMPLIANCE & HARDENING -->
<div class="page-break"></div>
<h1>7. Security Hardening, CERT-In &amp; Regulatory Compliance</h1>

<h2>7.1 CERT-In Compliance Implementation</h2>
<table>
    <tr>
        <th>CERT-In Mandate</th>
        <th>Regulatory Requirement</th>
        <th>CSIR-SWA OS Implementation Mechanism</th>
    </tr>
    <tr>
        <td><strong>Mandatory NTP Sync</strong></td>
        <td>Connect to NPL India or NIC atomic clock servers</td>
        <td>Chrony daemon configured to <code>time.nplindia.org</code> and <code>ntp.nic.in</code>.</td>
    </tr>
    <tr>
        <td><strong>180-Day Log Retention</strong></td>
        <td>Retain system logs within Indian jurisdiction for rolling 180 days</td>
        <td>Dedicated <code>/var/log</code> subvolume with Snapper retention policy and zstd compression.</td>
    </tr>
    <tr>
        <td><strong>6-Hour Incident Reporting</strong></td>
        <td>Report incidents to CERT-In within 6 hours of discovery</td>
        <td>Local AI Security Center auto-formats incident dossiers with attack vectors, IOC hashes, and timelines.</td>
    </tr>
    <tr>
        <td><strong>Tamper-Evident Ledger</strong></td>
        <td>Cryptographic proof that logs have not been altered or deleted</td>
        <td>SHA-256 append-only hash-chained ledger on all events in <code>/var/log/audit/csir_audit.ledger</code>.</td>
    </tr>
</table>

<h2>7.2 Cryptographic Hash-Chain Ledger Formula</h2>
<p>
Every administrative action $R_i$ committed to <code>/var/log/audit/csir_audit.ledger</code> is cryptographically sealed:
</p>
<pre>Hash_i = SHA-256( Hash_{{i-1}} || Timestamp || Actor || IP || Action || Resource || Details )</pre>
<p>
The genesis block ($i=1$) uses $Hash_0 = \\text{{0000000000000000000000000000000000000000000000000000000000000000}}$. Any attempt to alter, delete, or inject an audit record invalidates all subsequent hashes, triggering an immediate security alert during <code>csir-ctl audit verify</code>.
</p>

<h2>7.3 Kernel Sysctl Hardening Baseline (`99-csir-security.conf`)</h2>
<pre># Process and Memory Protection
kernel.randomize_va_space = 2
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.yama.ptrace_scope = 2
kernel.unprivileged_bpf_disabled = 1
net.core.bpf_jit_harden = 2
fs.suid_dumpable = 0
fs.protected_hardlinks = 1
fs.protected_symlinks = 1

# Network Stack Hardening (SYN Flood &amp; Spoofing Defense)
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_rfc1337 = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1

# High-Concurrency Web Workload Limits
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 10240 65535</pre>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">Document Sign-off &amp; Release Attestation</div>
    <strong>Approved by:</strong> CSIR Secure Software Release Authority &amp; CSIR-SERC Engineering Working Group.<br>
    <strong>Release Checksum:</strong> SHA-256 verification matching release manifest <code>release/release-manifest.json</code>.<br>
    <strong>Classification:</strong> Official Institutional Specification — Council of Scientific and Industrial Research.
</div>

</body>
</html>
"""
    return html

def main():
    print("=====================================================================")
    print(" CSIR Secure Web Appliance OS - Full PDF Documentation Generator")
    print("=====================================================================")

    html_content = generate_html()
    print(f"[*] Writing HTML document to: {OUTPUT_HTML}...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    html_size = OUTPUT_HTML.stat().st_size
    print(f"[✓] HTML generated: {html_size:,} bytes ({html_size / 1024:.2f} KB)")

    if not Path(EDGE_PATH).exists():
        print(f"[!] Error: Microsoft Edge not found at {EDGE_PATH}")
        sys.exit(1)

    print(f"[*] Converting HTML to PDF via headless Microsoft Edge...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        f"--print-to-pdf={OUTPUT_PDF}",
        "--no-pdf-header-footer",
        f"file:///{str(OUTPUT_HTML).replace(os.sep, '/')}"
    ]

    subprocess.run(cmd, capture_output=True, text=True)

    if OUTPUT_PDF.exists() and OUTPUT_PDF.stat().st_size > 0:
        pdf_size = OUTPUT_PDF.stat().st_size
        pdf_bytes = OUTPUT_PDF.read_bytes()
        page_count = pdf_bytes.count(b"/Type /Page\n") + pdf_bytes.count(b"/Type /Page ") + pdf_bytes.count(b"/Type /Page/")
        print("=====================================================================")
        print(f"[SUCCESS] PDF DOCUMENT CREATED SUCCESSFULLY!")
        print(f" Location:   {OUTPUT_PDF}")
        print(f" Size:       {pdf_size:,} bytes ({pdf_size / (1024*1024):.2f} MB)")
        print(f" Total Pages:{page_count} pages")
        print("=====================================================================")
    else:
        print(f"[!] PDF file was not created or has 0 bytes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
