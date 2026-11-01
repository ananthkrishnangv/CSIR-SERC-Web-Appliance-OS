# CSIR Secure Web Appliance OS (CSIR-SWA OS)
### Immutable Web, Application and Security Platform based on openSUSE MicroOS
**Release Baseline:** 28 September 2026 | **Version:** 1.0.0 (Stable Channel)  
**Lead Organisation:** CSIR-SERC / Participating Laboratories  
**Image File:** `release/csir-swa-os-1.0.0-fullstack-x86_64.iso` (2.73 GB Monolithic Full-Stack Offline DVD)

---

## Table of Contents
1. [Product Overview & Architecture](#1-product-overview--architecture)
2. [Default Credentials & Authentication](#2-default-credentials--authentication)
3. [Backend Architecture, IP Addresses & Ports](#3-backend-architecture-ip-addresses--ports)
4. [All Configuration Options & Environment Variables](#4-all-configuration-options--environment-variables)
5. [Desktop & Virtual Machine Configuration Settings](#5-desktop--virtual-machine-configuration-settings)
6. [Appliance CLI Operations (`csir-ctl`)](#6-appliance-cli-operations-csir-ctl)
7. [Installation & Deployment Guide](#7-installation--deployment-guide)
8. [Compliance & Security Standards](#8-compliance--security-standards)

---

## 1. Product Overview & Architecture

**CSIR Secure Web Appliance OS (CSIR-SWA OS)** is an immutable, hardened appliance operating system engineered for hosting, securing, monitoring, and backing up institutional web portals, laboratory mini-sites, APIs, and scientific dashboards across CSIR institutions.

```text
[External Clients / Internet Traffic]
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│ 1. Web Delivery & Edge Security Plane                  │
│    • nftables default-deny host firewall               │
│    • HAProxy 3.0 / NGINX reverse proxy                 │
│    • Coraza WAF with OWASP Core Rule Set (CRS) v4      │
│    • Suricata 7.0 network IDS/IPS telemetry            │
└──────────────────────────┬─────────────────────────────┘
                           │ Proxied Socket
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Application & Workload Plane                        │
│    • Rootless Podman 6.1.2 with systemd Quadlets       │
│    • Dedicated user namespaces (csir-app:100000)       │
│    • Read-only container root & cap_drop=ALL           │
│    • Certified templates: Python, Node.js, PHP, Java   │
└────────────┬─────────────────────────────┬─────────────┘
             │                             │
             ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ 3. Immutable Base OS      │ │ 4. Management Plane       │
│    • openSUSE MicroOS core│ │    • UX4G Nuxt 4 / Vue 3  │
│    • Btrfs + Snapper      │ │    • FastAPI Control Plane│
│    • transactional-update │ │    • Privileged Node Agent│
│    • Cryptographic verify │ │    • OPA Policy Engine    │
└────────────┬──────────────┘ └────────────┬──────────────┘
             │                             │
             ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ 5. Data Protection Plane  │ │ 6. Local AI & Governance  │
│    • Btrfs subvolume snaps│ │    • Local AI Sec Center  │
│    • Restic deduplication │ │    • Threat Correlation   │
│    • PostgreSQL 17 PITR   │ │    • Hash-chained ledger  │
│    • Automated DR drills  │ │    • CERT-In 6h dossier   │
└───────────────────────────┘ └───────────────────────────┘
```

---

## 2. Default Credentials & Authentication

> [!IMPORTANT]
> Change all default administrative and database passwords immediately after the initial installation wizard completes or before deploying into an active network environment.

### 2.1 Management Web Portal & Control Plane
Access URL: `https://<APPLIANCE_IP>:8443/` or local dev `http://127.0.0.1:8000/`

| Account Role | Username / Identifier | Default Password | Default MFA TOTP | Access Scope & Permissions |
|---|---|---|---|---|
| **Super Administrator** | `admin` *(or `admin@csir.res.in`)* | `CsirWebOS@2026!` | `123456` | Full appliance administration, security policies, updates, system rollback |
| **Security Officer** | `sec-officer` | `SecOfficer@2026!` | `123456` | Audit ledger verification, CERT-In compliance export, WAF rule management |
| **Operations Operator** | `operator` | `Operator@2026!` | `123456` | Container deployment, service restarts, backup trigger, monitoring dashboards |
| **Audit Inspector** | `auditor` | `Auditor@2026!` | `123456` | Read-only inspection of cryptographic logs, compliance checklists, reports |

### 2.2 Operating System & Root Accounts
| Account | UID:GID | Default Password | Shell | Notes & Security Policy |
|---|---|---|---|---|
| **`root`** | `0:0` | Set during YaST install *(AutoYaST preset: `CsirRoot@2026!`)* | `/bin/bash` | System superuser. SSH login disabled by default. Console login only. |
| **`csir-app`** | `100000:65536` | *No interactive password* | `/sbin/nologin` | Rootless Podman service user. User namespaces mapped in `/etc/subuid` and `/etc/subgid`. |
| **`csir-swa`** | `998:998` | *No interactive password* | `/sbin/nologin` | System service daemon user running the FastAPI control plane. |

### 2.3 Database Credentials (PostgreSQL 17 & PgBouncer)
| Parameter | Default Value | Notes |
|---|---|---|
| **Database Host** | `127.0.0.1` *(or socket `/run/postgresql`)* | Restricted to loopback; never exposed externally |
| **Database Port** | `5432` | Standard PostgreSQL port |
| **Database Name** | `csir_swa_db` | Appliance metadata, workload records, policy state |
| **DB Superuser** | `postgres` | Maintenance & initial setup |
| **DB Superuser Pass** | `CsirPostgres@2026!` | Stored in secure root environment |
| **DB App User** | `csir_admin` | Dedicated control plane user |
| **DB App Password** | `CsirPgSecure@2026!` | SCRAM-SHA-256 authenticated |
| **Connection URI** | `postgresql://csir_admin:CsirPgSecure%402026%21@127.0.0.1:5432/csir_swa_db` | Configured via `DATABASE_URL` |
| **PgBouncer Port** | `6432` | Connection pooling port |
| **SQLite Fallback** | `sqlite:////var/lib/csir-swa/data/csir_swa.db` | Embedded local mode when standalone |

### 2.4 Cryptographic Keys & Backup Passphrases
| Key / Passphrase | Default / Preset Value | Storage Location |
|---|---|---|
| **JWT Secret Key** | `csir-swa-strategic-secure-key-2026-production` | `/etc/csir-swa/control-plane.env` (`CSIR_SECRET_KEY`) |
| **Audit Ledger Genesis** | `0000000000000000000000000000000000000000000000000000000000000000` | `/var/log/audit/csir_audit.ledger` |
| **Restic Backup Pass** | `CsirResticBackup@2026!` | `/etc/csir-swa/backup-keys/restic.key` (chmod 600) |
| **BorgBackup Pass** | `CsirBorgPass@2026!` | `/etc/csir-swa/backup-keys/borg.key` (chmod 600) |
| **TPM 2.0 Key Slot** | PCR 0, 2, 7 (Firmware, Bootloader, SecureBoot) | Hardware TPM 2.0 / LUKS2 volume header |

---

## 3. Backend Architecture, IP Addresses & Ports

### 3.1 Network Topology & Interfaces
```text
                     ┌───────────────────────────────────┐
                     │    CSIR-SWA Appliance Host        │
                     │                                   │
  [DMZ / Public] ───►│ eth1: 10.10.10.100 (Web Delivery) │
  (Ports 80, 443)    │                                   │
                     │ lo:   127.0.0.1 (IPC, DB, Proxy)  │
                     │                                   │
  [Internal / OAM]──►│ eth0: 192.168.1.100 (Management)  │
  (Ports 8443, 22)   └───────────────────────────────────┘
```

- **Interface `eth0` / `enp0s3` (Management & Administration Plane):**
  - **Static IP (Air-gapped / Recommended):** `192.168.1.100`
  - **Subnet Mask:** `255.255.255.0` (`/24`)
  - **Default Gateway:** `192.168.1.1`
  - **Primary DNS:** `192.168.1.1` *(Secondary: `1.1.1.1` / `8.8.8.8` / NIC DNS `164.100.1.1`)*
  - **DHCP Fallback:** If dynamic addressing is used, the appliance binds to the DHCP-assigned lease (e.g. `10.0.2.15` in standard VirtualBox NAT).
- **Interface `eth1` / `enp0s8` (Public / DMZ Web Traffic Plane):**
  - Configured for hosted research websites, APIs, and portals with Coraza WAF protection.
- **Interface `lo` (Loopback `127.0.0.1`):**
  - High-speed local inter-process communication between HAProxy, FastAPI, Node Agent, and PostgreSQL.

### 3.2 Service Matrix & Port Allocation
| Port | Protocol | Bound IP | Service Name | Purpose & Access Level |
|---|---|---|---|---|
| **`8443`** | TCP (HTTPS) | `0.0.0.0` | **UX4G Web Portal** | Management UI & Administration Console (TLS 1.3) |
| **`8000`** | TCP (HTTP) | `127.0.0.1` *(or `0.0.0.0`)* | **FastAPI Control Plane** | REST API backend, Swagger UI at `/docs` |
| **`80`** | TCP (HTTP) | `0.0.0.0` | **Edge Reverse Proxy** | Plain HTTP (Automatically redirects to HTTPS 443) |
| **`443`** | TCP (HTTPS) | `0.0.0.0` | **Coraza WAF + HAProxy** | Secured public delivery for research applications |
| **`5432`** | TCP | `127.0.0.1` | **PostgreSQL 17** | Internal database service |
| **`6432`** | TCP | `127.0.0.1` | **PgBouncer** | Connection pooling for high concurrency |
| **`9090`** | TCP (HTTP) | `127.0.0.1` | **Prometheus** | Metrics scraper (node exporter, podman metrics) |
| **`3000`** | TCP (HTTP) | `127.0.0.1` | **Grafana** | Visual dashboards for telemetry and system health |
| **`3100`** | TCP (HTTP) | `127.0.0.1` | **Grafana Loki** | Log ingestion pipeline |
| **`4222`** | TCP | `127.0.0.1` | **NATS JetStream** | Async event broker & job queue |
| **`6379`** | TCP | `127.0.0.1` | **Redis (Optional)** | Rate limiting and fast caching |
| **`22`** | TCP (SSH) | `0.0.0.0` | **OpenSSH Server** | Remote CLI (Disabled by default; toggleable via console) |
| **Unix Socket** | Local IPC | `/run/csir-swa/agent.sock` | **Privileged Node Agent** | Secure RPC socket with strict capability allowlist |

### 3.3 Core REST API Endpoints
All API routes are prefixed under `/api/v1`:

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/system/health` | Overall appliance health, immutable status, disk usage |
| `GET` | `/api/v1/overview/` | Dashboard metrics, active apps, security score, backup status |
| `POST` | `/api/v1/auth/login` | Authenticates administrator and returns JWT Bearer token |
| `GET` | `/api/v1/apps/` | Lists all deployed container workloads and quadlets |
| `POST` | `/api/v1/apps/deploy` | Deploys certified Podman quadlet workload (.container) |
| `GET` | `/api/v1/security/waf/status` | Coraza WAF status, blocked attack counters, OWASP CRS rules |
| `POST` | `/api/v1/security/waf/rules/toggle` | Enables/disables specific OWASP CRS protection rules |
| `GET` | `/api/v1/ai-security/insights` | Local AI threat correlation, RCA, and capacity forecast |
| `POST` | `/api/v1/ai-security/chatops` | Governed Natural Language ChatOps with human approval |
| `GET` | `/api/v1/audit/ledger` | Returns CERT-In tamper-evident audit ledger entries |
| `POST` | `/api/v1/audit/verify` | Validates SHA-256 cryptographic hash-chain integrity |
| `GET` | `/api/v1/backups/` | Lists Btrfs snapshots and encrypted Restic repositories |
| `POST` | `/api/v1/backups/dr-drill` | Executes sandbox automated disaster recovery restore drill |
| `GET` | `/api/v1/updates/status` | Transactional-update status, pending snapshots, rollback target |
| `POST` | `/api/v1/updates/stage` | Stages signed OS update via transactional-update |

---

## 4. All Configuration Options & Environment Variables

### 4.1 Appliance Environment File (`/etc/csir-swa/control-plane.env`)
The FastAPI control plane loads its configuration from this environment file:

```ini
#=============================================================================
# CSIR Secure Web Appliance OS - Control Plane Environment Configuration
# Location: /etc/csir-swa/control-plane.env
#=============================================================================

# Product Information
PROJECT_NAME="CSIR Secure Web Appliance OS"
APP_VERSION="1.0.0"
API_V1_STR="/api/v1"

# Storage & Directory Paths
CSIR_DATA_DIR="/var/lib/csir-swa/data"
CSIR_LOG_DIR="/var/lib/csir-swa/data/logs"
CSIR_AUDIT_LEDGER="/var/log/audit/csir_audit.ledger"
CSIR_BACKUP_DIR="/srv/backups"
CSIR_TEMPLATES_DIR="/srv/apps"

# Database Configuration (PostgreSQL 17 / SQLite)
DATABASE_URL="postgresql://csir_admin:CsirPgSecure%402026%21@127.0.0.1:5432/csir_swa_db"
# Fallback for standalone/embedded:
# DATABASE_URL="sqlite:////var/lib/csir-swa/data/csir_swa.db"

# Security & Session Tokens
CSIR_SECRET_KEY="csir-swa-strategic-secure-key-2026-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="480"

# Privileged Node Agent Socket
NODE_AGENT_SOCKET="/run/csir-swa/agent.sock"
NODE_AGENT_MOCK="false"

# Lifecycle & Release Channel (Options: LTS, Stable, Pilot, Security, Emergency, Air-gap)
CURRENT_CHANNEL="Stable"

# CERT-In Compliance Parameters
CERT_IN_REPORTING_HOURS="6"
LOG_RETENTION_DAYS="180"
NTP_SERVERS="time.nplindia.org,ntp.nic.in"

# Hardware Security & Health
ENABLE_TPM_SEALING="true"
ENABLE_HEALTH_GATES="true"
HEALTH_GATE_SCRIPT="/usr/lib/csir-swa/bin/csir-health-gate.sh"
```

### 4.2 Network Configuration Options (`systemd-networkd`)
Static IP configuration file for `/etc/systemd/network/10-management.network`:

```ini
[Match]
Name=enp0s3 eth0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=192.168.1.1
DNS=1.1.1.1
NTP=time.nplindia.org ntp.nic.in
```

For DHCP environments, use:
```ini
[Match]
Name=enp0s3 eth0

[Network]
DHCP=yes
```

### 4.3 Snapper & Transactional Update Policy
- **Snapper Configuration (`/etc/snapper/configs/root`):**
  ```ini
  SUBVOLUME="/"
  FSTYPE="btrfs"
  TIMELINE_CREATE="yes"
  TIMELINE_CLEANUP="yes"
  TIMELINE_MIN_AGE="1800"
  TIMELINE_LIMIT_HOURLY="10"
  TIMELINE_LIMIT_DAILY="7"
  TIMELINE_LIMIT_WEEKLY="4"
  TIMELINE_LIMIT_MONTHLY="12"
  NUMBER_LIMIT="10"
  NUMBER_LIMIT_IMPORTANT="5"
  ```
- **Transactional Update Policy (`/etc/transactional-update.conf`):**
  ```ini
  REBOOT_METHOD="systemd"
  UPDATE_ALLOW_AUTOMATIC_REBOOT="no"
  HEALTH_CHECK_SCRIPT="/usr/lib/csir-swa/bin/csir-health-gate.sh"
  ROLLBACK_ON_FAILURE="yes"
  ```

### 4.4 Firewall Configuration (`/etc/nftables/csir-firewall.nft`)
Default-deny host firewall protecting the appliance:
```nftables
table inet csir_filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # Allow established and related traffic
        ct state established,related accept

        # Allow loopback interface
        iif "lo" accept

        # Allow ICMP / Ping (Rate limited)
        ip protocol icmp limit rate 10/second accept

        # Web Delivery & Reverse Proxy
        tcp dport { 80, 443 } accept

        # UX4G Management Console (Restrict to OAM subnet in production)
        tcp dport 8443 accept

        # Optional SSH (Disabled by default)
        # tcp dport 22 accept
    }
}
```

---

## 5. Desktop & Virtual Machine Configuration Settings

> [!WARNING]
> **YaST Graphical Installer RAM Requirement:**  
> The YaST Graphical Easy Installer requires a minimum of **2048 MB RAM** (4096 MB recommended).  
> If allocated **1024 MB RAM or less**, openSUSE MicroOS will automatically fall back to the blue text-mode `linuxrc` installer. Ensure your VM is provisioned with at least 4096 MB RAM.

### 5.1 Virtual Machine Hardware Sizing Matrix
| Sizing Tier | vCPUs | RAM (Memory) | Video Memory (VRAM) | Storage (Disk) | Recommended Use Case |
|---|---|---|---|---|---|
| **Minimum Testing** | 2 vCPUs | 2048 MB | 64 MB | 30 GB SSD | Basic ISO validation & CLI testing |
| **Standard Development** | 4 vCPUs | **4096 MB** | **128 MB** | 50 GB SSD | **Recommended for GUI Installer & Portal** |
| **Production Appliance** | 8 vCPUs | 16384 MB | 128 MB | 250 GB NVMe | Hosting 10+ Podman Quadlets & WAF |

### 5.2 VirtualBox Recommended Configuration
#### Method A: Graphical Settings (GUI)
1. **System -> Motherboard:**
   - Base Memory: **4096 MB**
   - Chipset: **ICH9** or **PIIX3**
   - Extended Features: Check **Enable I/O APIC**, Check **Enable EFI** (optional, supported in BIOS & EFI)
2. **System -> Processor:**
   - Processors: **4 CPUs**
   - Execution Cap: **100%**
   - Extended Features: Check **Enable PAE/NX**
3. **Display -> Screen:**
   - Video Memory: **128 MB** (Slide slider to maximum 128 MB)
   - Graphics Controller: **VBoxSVGA** *(or **VMSVGA**)*
   - Extended Features: Check **Enable 3D Acceleration**
4. **Storage:**
   - Controller: SATA (or NVMe)
   - Optical Drive: Attach `csir-swa-os-1.0.0-fullstack-x86_64.iso`
   - Hard Disk: Minimum 40.00 GB (Dynamic VDI)
5. **Network -> Adapter 1:**
   - Attached to: **Bridged Adapter** *(Access directly on LAN IP)*  
     *OR*
   - Attached to: **NAT** with the following **Port Forwarding Rules**:
     | Name | Protocol | Host IP | Host Port | Guest IP | Guest Port |
     |---|---|---|---|---|---|
     | `csir_portal` | TCP | `127.0.0.1` | `8443` | `10.0.2.15` | `8443` |
     | `csir_fastapi` | TCP | `127.0.0.1` | `8000` | `10.0.2.15` | `8000` |
     | `csir_http` | TCP | `127.0.0.1` | `8080` | `10.0.2.15` | `80` |
     | `csir_https` | TCP | `127.0.0.1` | `8444` | `10.0.2.15` | `443` |

#### Method B: One-Liner PowerShell / CLI Script
To configure an existing VirtualBox VM named `SUSEENTERPRISE`:
```powershell
VBoxManage modifyvm "SUSEENTERPRISE" --memory 4096 --cpus 4 --vram 128 --graphicscontroller vmsvga --accelerate3d on
```

To create a fresh VM from scratch:
```powershell
$VM = "CSIR-WebOS-Appliance"
$ISO = "D:\Documents C Drive\Deployment-Servers\CSIRWebOS\release\csir-swa-os-1.0.0-fullstack-x86_64.iso"

VBoxManage createvm --name $VM --ostype "OpenSUSE_64" --register
VBoxManage modifyvm $VM --memory 4096 --cpus 4 --vram 128 --graphicscontroller vmsvga --accelerate3d on
VBoxManage createhd --filename "$HOME\VirtualBox VMs\$VM\$VM.vdi" --size 51200
VBoxManage storagectl $VM --name "SATA" --add sata --controller IntelAhci --portcount 2
VBoxManage storageattach $VM --storagectl "SATA" --port 0 --device 0 --type hdd --medium "$HOME\VirtualBox VMs\$VM\$VM.vdi"
VBoxManage storageattach $VM --storagectl "SATA" --port 1 --device 0 --type dvddrive --medium $ISO
VBoxManage modifyvm $VM --nic1 nat
VBoxManage modifyvm $VM --natpf1 "portal,tcp,,8443,,8443"
VBoxManage modifyvm $VM --natpf1 "fastapi,tcp,,8000,,8000"
VBoxManage startvm $VM
```

### 5.3 VMware Workstation / ESXi Recommended Settings
- **Guest Operating System:** Linux -> `openSUSE 64-bit` (or `Other Linux 6.x kernel 64-bit`)
- **Memory:** 4096 MB
- **Processors:** 2 sockets, 2 cores per socket (4 total vCPUs)
- **Display:** Check **Accelerate 3D graphics**, Graphics memory: **128 MB** (or 256 MB)
- **Virtual Disk:** 50 GB SCSI (Single file, Non-split)
- **Firmware:** UEFI (Recommended)

### 5.4 Display Resolutions & Console Function Keys
- **Display Resolution Support:**
  - Installer Resolution: `1024x768` (Default standard 4:3)
  - Widescreen Resolutions: `1280x800`, `1440x900`, `1920x1080` (Auto-adapted by VMSVGA / Wayland)
- **Appliance Console Shortcut Keys:**
  - **`F2`**: Appliance Administration Menu (Network config, password reset, reboot)
  - **`F8`**: Disaster Recovery & Btrfs Snapshot Rollback Menu
  - **`Ctrl + Alt + F2`**: Root Diagnostic Shell (Maintenance terminal)
  - **`Ctrl + Alt + F3`**: YaST Installation Log Viewer
  - **`Ctrl + Alt + F4`**: Linux Kernel dmesg / hardware events
  - **`Ctrl + Alt + F7`**: Graphical Installer / Wayland UI Console

### 5.5 Client Web Browser Requirements
- **Supported Browsers:**
  - Google Chrome / Chromium $\ge$ 115
  - Mozilla Firefox $\ge$ 120
  - Microsoft Edge $\ge$ 115
  - Apple Safari $\ge$ 17
- **Bypassing Self-Signed Appliance TLS Warning:**
  - When accessing `https://<APPLIANCE_IP>:8443` for the first time, browsers display a self-signed certificate warning.
  - **Chrome / Edge:** Click **Advanced** $\to$ **Proceed to <IP> (unsafe)**, or type `thisisunsafe` directly into the page.
  - **Firefox:** Click **Advanced** $\to$ **Accept the Risk and Continue**.

---

## 6. Appliance CLI Operations (`csir-ctl`)

The unified CLI tool `csir-ctl` provides direct administrative capabilities from the terminal:

```bash
# Check overall appliance status and active release channel
python backend/cli/csir_ctl.py status

# List all hosted container applications
python backend/cli/csir_ctl.py apps list

# Deploy a new Quadlet container workload
python backend/cli/csir_ctl.py apps deploy \
    --name "CSIR Research Portal" \
    --image "registry.csir.res.in/portal/research:1.0" \
    --port 8088 \
    --domain "research.csir.res.in"

# Verify cryptographic audit ledger integrity (detects tampering)
python backend/cli/csir_ctl.py audit verify

# Export CERT-In compliant incident package
python backend/cli/csir_ctl.py audit cert-in

# Execute automated disaster recovery restore drill
python backend/cli/csir_ctl.py backup dr-drill
```

---

## 7. Installation & Deployment Guide

### 7.1 Automated Monolithic Full-Stack ISO Build
The bootable Monolithic Full-Stack DVD ISO is compiled via `remaster-full-dvd.py`:
```powershell
python -u iso-builder/remaster-full-dvd.py
```
This produces:
- **Output:** `release/csir-swa-os-1.0.0-fullstack-x86_64.iso` (2.73 GB)
- **Checksum:** `release/csir-swa-os-1.0.0-fullstack-x86_64.iso.sha256`
- **Manifest:** `release/release-manifest.json`

### 7.2 Boot Menu Options
Upon booting the DVD ISO, the bootloader offers three distinct deployment modes:
1. **Install CSIR Secure Web Appliance OS (GUI Easy Installer) [Default]:**
   - Boots directly into the graphical YaST installer with Combustion hooks.
   - Interactive language selection, keyboard mapping, root password setup, and disk layout.
2. **Install CSIR Secure Web Appliance OS (Automated Express Installation):**
   - Zero-touch automated installation using `/autoyast/autoinst.xml`.
   - Automatically partitions disk with Btrfs root, installs all CSIR features, and reboots.
3. **Install CSIR-SWA OS (Hardened Strategic Air-Gapped Mode):**
   - High-security offline profile: disables external network discovery, enables strict local repo only.
4. **CSIR Rescue & Recovery System:**
   - Live maintenance environment for mounting Btrfs snapshots, resetting passwords, and repairing bootloaders.

### 7.3 Alternative Universal Script-based Appliance Converter
For systems already deployed on **openSUSE MicroOS**, **openSUSE Leap / Tumbleweed**, **Rocky Linux 8/9/10**, **AlmaLinux 8/9/10**, or **Fedora Linux**, convert the OS in-place into a hardened CSIR-SERC appliance:

#### Method A: Dedicated openSUSE MicroOS Transactional Converter (Recommended for MicroOS)
MicroOS uses an immutable read-only root and atomic Btrfs snapshots. The specialized `convert-microos.sh` stages the full appliance stack via `transactional-update` without breaking immutability:
```bash
cd installer
# Interactive MicroOS conversion:
sudo ./convert-microos.sh

# Unattended automated full-stack conversion with reboot:
sudo ./convert-microos.sh --unattended --all --reboot

# Convert to Edge WAF appliance profile:
sudo ./convert-microos.sh --profile edge-waf --reboot
```

#### Method B: Universal Online Remote Bootstrap
No git installation or repository cloning required. The bootstrap script automatically streams and unpacks the appliance payload via `curl`/`wget` and `tar`, automatically detects openSUSE MicroOS vs standard Linux, and executes the appropriate transactional or modular engine:
```bash
# Interactive conversion (Terminal-aware):
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash

# Unattended full-stack conversion with automated reboot:
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash -s -- --unattended --all --reboot

# Specific deployment profile (e.g. Edge WAF):
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash -s -- --profile edge-waf --reboot

# Using environment variables (Ideal for cloud-init / post-install hooks):
export CSIR_PROFILE="full" CSIR_UNATTENDED="true" CSIR_REBOOT="true"
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo -E bash
```

#### Method C: Post-Installation Automation (After OS Installation Over)
Pre-configured templates in `installer/post-install/` allow zero-touch provisioning immediately after OS installation finishes:
- **Combustion Hook (`installer/post-install/combustion/script`):** openSUSE MicroOS / SUSE Linux Micro initramfs first-boot drive hook.
- **Systemd First-Boot Unit (`installer/post-install/csir-firstboot.service`):** Generic systemd unit for pre-baked VM templates and images.
- **Cloud-Init (`installer/post-install/cloud-init/user-data.yaml`):** Automated bootstrap in Proxmox, VMware, OpenStack, and cloud providers.
- **AutoYaST Snippet (`installer/post-install/autoyast-snippet.xml`):** Chroot post-install hook for openSUSE YaST answer files.

#### Method C: Universal Interactive Wizard (Standard Linux Systems)
```bash
cd installer
sudo ./setup-appliance.sh
```

#### Method D: Unattended Automated Installation
```bash
# Automated Full-Stack Installation:
sudo ./installer/setup-appliance.sh --unattended --all

# Automated Edge WAF Reverse Proxy:
sudo ./installer/setup-appliance.sh --unattended --profile edge-waf
```

---

## 8. Compliance & Security Standards

- **CERT-In Compliance:**
  - **180-Day Log Retention:** All audit records stored with SHA-256 hash chaining.
  - **6-Hour Reporting:** Pre-formatted incident dossiers generated via `csir-ctl audit cert-in`.
  - **NTP Time Synchronization:** Traceable to National Physical Laboratory (NPL) India atomic clocks.
- **GIGW (Guidelines for Indian Government Websites):**
  - Accessibility compliance, TLS 1.3 enforcement, OWASP Top 10 mitigation via Coraza WAF.
- **ISO 27001:**
  - Access control separation (Super Admin, Security Officer, Operator).
  - Immutable operating system with automated rollback on health check failure.

---

## 9. CI/CD Integration & Automated Release Pipeline

The project features a full continuous integration and deployment pipeline via GitHub Actions:
- **Continuous Integration (`.github/workflows/ci.yml`):**
  - Runs automated pytest test suite across Python 3.12 and 3.13.
  - Validates all installer shell scripts syntax with `bash -n`.
  - Packages and validates `csir-appliance-installer-v1.0.0.tar.gz` build artifact with SHA-256 verification.
- **Release Automation (`.github/workflows/release.yml`):**
  - Automatically triggers on version tags (`v*`).
  - Packages and publishes standalone installer release assets and checksums to GitHub Releases.

