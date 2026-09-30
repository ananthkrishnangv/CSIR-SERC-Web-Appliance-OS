# CSIR Secure Web Appliance OS (CSIR-SWA OS)
## Architectural Specification and Engineering Manual
**Version:** 1.0.0 (Release Baseline: 28 September 2026)  
**Lead Organisation:** CSIR-SERC / CSIR Labs

---

## 1. Product Overview & Principles

CSIR Secure Web Appliance OS (**CSIR-SWA OS**) is a specialized, immutable, transactionally updated appliance engineered to host, protect, monitor, and recover public websites, scientific portals, research dashboards, APIs, and containerized microservices across CSIR laboratories.

### Core Architectural Principles
1. **Immutable by Default:** The root operating system is mounted read-only. Updates are applied transactionally via Btrfs snapshots and activated via staged reboot with automatic rollback if health gates fail.
2. **Six Isolated Planes:**
   - **Immutable Operating System Plane:** MicroOS core, Btrfs, Snapper, transactional-update.
   - **Management & Policy Plane:** Nuxt 4 portal, Python 3.14 FastAPI control plane, OPA policy engine, PostgreSQL, NATS JetStream.
   - **Application & Container Plane:** Rootless Podman 6.1.2, systemd Quadlet definitions, isolated user namespaces, read-only container roots.
   - **Delivery & Security Plane:** Edge reverse proxy (HAProxy), Coraza WAF with OWASP Core Rule Set (CRS) v4, nftables host firewall, Suricata network IDS/IPS.
   - **Backup & Recovery Plane:** Btrfs volume snapshots, Restic deduplicated encrypted repositories, PostgreSQL PITR, immutable WORM export.
   - **Operations & Local AI Plane:** OpenTelemetry pipeline, CERT-In compliant tamper-evident hash-chained audit ledger, Local AI Security Center for anomaly correlation and evidence-backed mitigation recommendations.
3. **Privileged Agent Boundary:** The management API never executes unrestricted arbitrary shell commands. Privileged actions must match strictly typed, allow-listed tasks executed by the isolated Node Agent.
4. **Local-First AI:** All AI telemetry processing, embedding, anomaly scoring, and RAG operations remain on-premise within Indian infrastructure. AI acts exclusively as an advisory layer; mitigations require human confirmation based on risk tier.
5. **Recoverability & Evidence by Design:** Every administrative change is committed to a cryptographically linked, append-only audit trail meeting CERT-In requirements.

---

## 2. Filesystem & Storage Hierarchy

```text
/                                    [Read-only, Btrfs root snapshot]
├── /usr                             [Read-only system binaries]
├── /boot                            [Kernel, initrd, GRUB2 configuration]
├── /etc                             [Participates in system snapshots via overlay/Btrfs]
│   ├── csir-swa/                    [Appliance configuration manifests]
│   ├── containers/systemd/          # Rootful infrastructure quadlets
│   └── snapper/configs/root         [Snapper snapshot settings]
├── /var                             [Persistent writable subvolume]
│   ├── lib/containers/storage       [Podman images, layers, and volumes]
│   ├── lib/csir-swa/                [Appliance management database & state]
│   ├── lib/security-events/         [Suricata & WAF event spool]
│   └── log/audit/                   [Append-only hash-chained audit logs]
└── /srv                             [Appliance persistent application data]
    ├── apps/                        [Declarative application manifests]
    ├── app-data/                    [Application persistent subvolumes]
    ├── backups/                     [Local backup cache & staging]
    ├── repository/                  [Signed offline update & image mirror]
    └── models/                      [Local AI models, weights, and indexes]
```

---

## 3. Communication & Data Flow

```text
[External Clients / Internet]
           │
           ▼
┌───────────────────────────────┐
│ Edge nftables Firewall        │
└──────────┬────────────────────┘
           │ (Port 80/443)
           ▼
┌───────────────────────────────┐
│ HAProxy Reverse Proxy         │
└──────────┬────────────────────┘
           │ (Internal Spool)
           ▼
┌───────────────────────────────┐
│ Coraza WAF (OWASP CRS v4)     │
└──────────┬────────────────────┘
           │ (Reverse Proxied Socket)
           ▼
┌───────────────────────────────────────────────┐
│ Rootless Podman Workload (App User Slice)     │
│ - Read-Only Root                              │
│ - Dropped Capabilities (cap_drop = ALL)       │
│ - Dedicated User Namespace                    │
└──────────┬────────────────────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│ Persistent Data Subvolumes    │
│ (/srv/app-data/<app-id>)      │
└───────────────────────────────┘
```

---

## 4. Control Plane Architecture

The Management Plane is strictly decoupled:
- **Frontend:** Nuxt 4 (Vue 3, TypeScript, Pinia, Tailwind/UX4G-aligned CSS). Port 8443 (HTTPS).
- **Backend API:** FastAPI (Python 3.14.7). Port 8000 (Internal loopback/management network).
- **Node Agent:** High-integrity daemon listening on Unix domain socket `/run/csir-swa/agent.sock`. Validates cryptographically signed or token-authenticated IPC messages against an explicit allow-list:
  - `systemd_service_action(service, action)`
  - `snapper_create_snapshot(description, cleanup_type)`
  - `snapper_rollback(snapshot_id)`
  - `restic_run_backup(profile)`
  - `nftables_reload_rules()`
  - `support_bundle_generate()`
- **Audit Subsystem:** Every API mutation computes `SHA256(prev_hash + timestamp + user + action + payload)` to ensure zero undetected tampering.
