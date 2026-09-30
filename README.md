# CSIR Secure Web Appliance OS (CSIR-SWA OS)
### Immutable Web, Application and Security Platform based on openSUSE MicroOS
**Release Baseline:** 28 September 2026 | **Version:** 1.0.0 (Stable Channel)  
**Lead Organisation:** CSIR-SERC / Participating Laboratories

---

## 1. Executive Summary & Mission

**CSIR Secure Web Appliance OS (CSIR-SWA OS)** is a preconfigured, immutable, transactionally updated appliance engineered to host, protect, monitor, and recover public websites, research portals, laboratory mini-sites, recruitment/event portals, APIs, and scientific dashboards across CSIR institutions.

It replaces ad-hoc server administration with an immutable, governed appliance model:
- **Read-Only Root Filesystem:** Transactionally updated via Btrfs snapshots and Snapper with automated rollback.
- **Rootless Container Workloads:** Daemonless Podman 6.1.2 with systemd Quadlets, dropped Linux capabilities, and read-only container filesystems.
- **Defence-in-Depth Web Delivery:** HAProxy reverse proxy, Coraza WAF with OWASP Core Rule Set (CRS) v4, nftables host firewall, and Suricata network IDS/IPS.
- **Local AI Security Center:** On-premise evidence-grounded threat synthesis, anomaly correlation, MITRE ATT&CK mapping, and human-in-the-loop mitigation workflows.
- **Data Protection & DR:** Btrfs snapshots, Restic encrypted deduplicated backups, PostgreSQL PITR, and automated disaster recovery restore drills.
- **CERT-In Compliance:** Append-only SHA-256 hash-chained tamper-evident audit ledger, 180-day log retention, and 6-hour incident dossier generation.

---

## 2. Six Logical Planes Architecture

```text
[External Clients / Internet]
           │
           ▼
┌───────────────────────────────────────────────┐
│ 4. Web Delivery & Security Plane              │
│ - nftables default-deny host firewall         │
│ - HAProxy reverse proxy (TLS termination)     │
│ - Coraza WAF with OWASP CRS v4                │
│ - Suricata network IDS/IPS sensor             │
└──────────────────────┬────────────────────────┘
                       │ Proxied Socket
                       ▼
┌───────────────────────────────────────────────┐
│ 3. Application & Workload Plane               │
│ - Rootless Podman 6.1.2                       │
│ - systemd Quadlets (.container, .network)     │
│ - User namespaces (csir-app)                  │
│ - Read-only root & cap_drop=ALL               │
└──────────────────────┬────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ 1. Immutable OS Plane   │ │ 2. Management Plane     │
│ - openSUSE MicroOS core │ │ - Nuxt 4 / Vue 3 Portal │
│ - Btrfs + Snapper       │ │ - Python 3.14 FastAPI   │
│ - transactional-update  │ │ - Privileged Node Agent │
│ - Health gates          │ │ - OPA policy guardrails │
└─────────────────────────┘ └─────────────────────────┘
         │                           │
         ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ 5. Data Protection      │ │ 6. Observability & AI   │
│ - Btrfs volume snapshot │ │ - Local AI Sec Advisor  │
│ - Restic WORM repository│ │ - Hash-chained audit log│
│ - DR restore drills     │ │ - CERT-In reporting     │
└─────────────────────────┘ └─────────────────────────┘
```

---

## 3. Repository Structure

```text
CSIRWebOS/
├── appliance-os/                     # WP2: KIWI NG 9 build definition & OS overlays
│   ├── kiwi/
│   │   ├── config.xml                # KIWI appliance definition for openSUSE MicroOS
│   │   ├── config.sh                 # Pre-image configuration script
│   │   ├── images.sh                 # Post-package installation cleanup
│   │   └── root/                     # Appliance rootfs overlay (/etc, /usr, /srv)
│   ├── firstboot/                    # Combustion & first-boot wizard scripts
│   ├── boot/                         # GRUB2 theme & console boot screen
│   └── build-appliance.sh            # KIWI image build runner
├── backend/                          # WP3-WP8: FastAPI Control Plane & Node Agent
│   ├── app/
│   │   ├── main.py                   # FastAPI application factory & static mount
│   │   ├── config.py                 # Configuration settings
│   │   ├── database.py               # SQLAlchemy database session
│   │   ├── models/                   # ORM models (Apps, Security, AI, Backups, Audit)
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── api/                      # REST API endpoints (overview, apps, sec, ai, audit)
│   │   ├── services/                 # Services (Podman, WAF, AI, Backups, Updates, Audit)
│   │   ├── core/                     # Security, OPA policy engine, telemetry
│   │   └── static/                   # Interactive Management Portal Single-Page Application
│   ├── node_agent/                   # Privileged Node Agent (Strict allow-list boundary)
│   │   └── agent.py
│   ├── cli/                          # WP9: csir-appliance CLI
│   │   └── csir_ctl.py
│   └── tests/                        # 13 Automated pytest integration & unit tests
├── frontend/                         # WP3: Nuxt 4 / Vue 3 Management Portal Source
│   ├── package.json
│   ├── nuxt.config.ts
│   ├── tsconfig.json
│   ├── pages/index.vue               # Nuxt 4 landing dashboard matching Section 8 mockup
│   └── locales/                      # Localization (en.json, hi.json, ta.json)
├── templates/                        # WP4: Certified Podman Quadlet Application Templates
│   ├── csir-research-portal/         # Scientific Research Portal Quadlet
│   └── laboratory-api/               # High-Throughput Instrumentation API Quadlet
├── security-profiles/                # WP5: WAF, Suricata & Firewall Profiles
│   ├── coraza/                       # Coraza WAF & OWASP CRS v4 rules
│   ├── suricata/                     # Suricata EVE telemetry configuration
│   └── nftables/                     # Host default-deny firewall ruleset
└── docs/                             # WP1: Governance, Architecture & Compliance
    ├── ARCHITECTURE.md
    ├── THREAT_MODEL.md
    ├── CERT_IN_COMPLIANCE.md
    ├── AIRGAP_PROCEDURES.md
    └── ADR/                          # Architecture Decision Records (001 to 004)
```

---

## 4. Quick Start: Running the Control Plane & Portal

### 1. Launch the Backend API and Management Console
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at:
- **Management Console:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Run the Automated Test Suite
```bash
python -m pytest backend/tests -v
```
All 13 test suites verify:
- Tamper-evident hash-chained audit ledger creation and tamper detection
- Rootless Podman Quadlet generation with dropped capabilities
- Node Agent privileged allowlist boundary
- Local AI Security threat correlation and human approval guardrails
- REST API deployment flows, WAF rule toggling, and health checks

### 3. Using the Unified Appliance CLI (`csir-ctl`)
```bash
# View appliance status and version
python backend/cli/csir_ctl.py status

# List container workloads
python backend/cli/csir_ctl.py apps list

# Deploy a new workload
python backend/cli/csir_ctl.py apps deploy --name "New Portal" --image "registry.csir.res.in/apps/portal:1.0" --port 8088 --domain "portal.csir.res.in"

# Verify cryptographic audit ledger integrity
python backend/cli/csir_ctl.py audit verify

# Export CERT-In compliant audit package
python backend/cli/csir_ctl.py audit cert-in

# Run sandbox disaster recovery restore drill
python backend/cli/csir_ctl.py backup dr-drill
```

---

## 5. Building the Bootable Appliance OS Image (KIWI NG 9)

```bash
cd appliance-os
./build-appliance.sh single-node
```
Outputs bootable hybrid ISO (`.iso`) and raw virtual disk image (`.raw` / `.qcow2`) configured with openSUSE MicroOS, read-only Btrfs layout, transactional updates, first-boot wizard, and approved CSIR branding.
