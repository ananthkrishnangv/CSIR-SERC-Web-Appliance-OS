# CERT-In Compliance & Log Governance Matrix
**Reference:** CERT-In Directions under Sub-section (6) of Section 70B of the IT Act, 2000  
**Target:** CSIR Research Institutions & Strategic Deployment Nodes

---

## 1. Compliance Checklist & Implementation

| CERT-In Requirement | Specific Mandate | CSIR-SWA OS Implementation Mechanism | Status |
|---|---|---|---|
| **Mandatory NTP Sync** | Connect to National Physical Laboratory (NPL) or NIC NTP servers | `systemd-timesyncd` pre-configured to `time.nplindia.org` and `ntp.nic.in` with fallback to authenticated local PTP/NTP sources. | **Compliant** |
| **Log Retention (180 Days)** | Maintain system and security logs within Indian jurisdiction for rolling 180 days | Dedicated `/var/log` Btrfs subvolume with Snapper retention policy; automated rotation, zstd compression, and automated export to append-only WORM repository. | **Compliant** |
| **6-Hour Incident Reporting** | Cyber incidents must be reported to CERT-In within 6 hours of noticing | Local AI Security Center automatically generates CERT-In format incident dossiers (`incident-dossier-<id>.json` / `.pdf`), highlighting affected IPs, attack vectors, IOC hashes, and timelines. | **Compliant** |
| **Tamper-Evident Audit** | Proof that logs have not been altered or purged by an adversary | Cryptographic SHA-256 hash-chain ledger on all administrative events (`prev_hash` validation). Daily digital signature over the audit head. | **Compliant** |
| **Subscriber / User KYC** | Identity verification for administrative accounts | Centralized OIDC / LDAP integration, TOTP/WebAuthn hardware key enforcement, session recording for privileged break-glass operations. | **Compliant** |

---

## 2. Cryptographic Hash-Chain Formula

Each audit record $R_i$ is committed as:
$$\text{Hash}_i = \text{SHA256}(\text{Hash}_{i-1} \parallel \text{Timestamp} \parallel \text{Actor} \parallel \text{Action} \parallel \text{Resource} \parallel \text{Details})$$

Where $\text{Hash}_0$ is the Genesis hash generated at system provisioning. Any alteration, deletion, or insertion breaks the chain at index $i$, instantly alerting the auditor during verification.
