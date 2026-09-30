# Threat Model: CSIR Secure Web Appliance OS (CSIR-SWA OS)
**Framework:** STRIDE-per-Element & MITRE ATT&CK for Enterprise  
**Author:** CSIR Cyber Security Architecture Team  
**Classification:** Controlled Internal Document

---

## 1. STRIDE Analysis Matrix

| Threat Category | Potential Vector | Impact | Mitigation in CSIR-SWA OS |
|---|---|---|---|
| **Spoofing** | Forged administrative access, spoofed internal services | High | WebAuthn/FIDO2 MFA, short-lived signed JWTs, mutual TLS between management microservices, SSH CA certificates. |
| **Tampering** | Modification of OS files, container escape to host, tampering with audit trail | Critical | Read-only Btrfs root filesystem, SELinux/AppArmor profiles, rootless Podman with dropped capabilities (`cap_drop=ALL`), cryptographically linked SHA-256 audit ledger. |
| **Repudiation** | Administrator denies executing destructive change or disabling security filter | High | Immutable append-only audit trail capturing user ID, IP address, timestamp, pre/post state hash, and signed approval token. |
| **Information Disclosure** | Leakage of private lab data, leaked API keys, unauthorized memory dumps | High | LUKS2 full-disk/volume encryption, runtime secrets injection via OpenBao/systemd-creds (never baked into container images), strict nftables egress rules. |
| **Denial of Service** | Volumetric SYN flood, Slowloris HTTP attacks, algorithmic complexity attacks | High | nftables SYN proxy, HAProxy connection rate-limiting, Coraza request inspection buffers, cgroup v2 resource limits (CPU/Memory/IO quotas). |
| **Elevation of Privilege** | Container breakout, command injection in web UI to execute arbitrary shell | Critical | FastAPI backend cannot spawn arbitrary bash shells. Privileged tasks are strictly offloaded via typed, allow-listed IPC to the isolated Node Agent. |

---

## 2. Attack Trees & Defensive Gates

### Vector 1: Web Application Compromise (e.g., Log4Shell, SQLi, File Inclusion)
1. Ingress traffic is scanned by **Coraza WAF** with OWASP CRS v4.
2. In-depth network anomaly is tracked by **Suricata IDS** generating EVE JSON telemetry.
3. If an attacker breaches the application layer, they land in an isolated **rootless Podman container** with a read-only filesystem and no root privileges on the host kernel.
4. Outbound lateral movement is blocked by dedicated container network namespaces (`nftables` egress filtering).
5. **Local AI Security Center** correlates the WAF anomaly + unexpected child process, escalates alert severity, and proposes temporary IP throttle/container isolation requiring admin approval.

### Vector 2: Host Operating System Compromise / Malicious Update
1. Update bundles must be signed by the CSIR Release Engineering private key.
2. `transactional-update` applies RPM packages into a detached Btrfs snapshot.
3. System reboots into the new snapshot and initiates **CSIR Health Gates**:
   - Verification of management service responsiveness
   - Verification of firewall and WAF rulesets
   - Storage and database integrity check
4. If any health gate fails, system performs an automatic reboot and rollback to the known-good previous snapshot.
