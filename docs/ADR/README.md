# Architecture Decision Record (ADR) Index

### ADR-001: Selection of openSUSE MicroOS & KIWI NG 9 for Immutable Base
- **Status:** Accepted
- **Context:** Individual server administration leads to configuration drift, missed security updates, and high recovery times.
- **Decision:** Base the CSIR appliance on openSUSE MicroOS (with SUSE Linux Micro 6.2 compatibility) built with KIWI NG 9. The OS features a read-only root filesystem, transactional updates using Btrfs snapshots, and Snapper-driven automated rollback.

### ADR-002: Rootless Podman 6.1.2 and systemd Quadlets for Workloads
- **Status:** Accepted
- **Context:** Docker daemon running as root presents severe container breakout risks. Kubernetes is overly complex and resource-heavy for standalone and compact edge laboratory deployments.
- **Decision:** Use daemonless rootless Podman 6.1.2. Define containers declaratively via systemd Quadlets (`.container`, `.network`, `.volume`). Quadlets integrate natively with systemd lifecycle, journald logging, cgroup v2 resource limits, and auto-restart policies.

### ADR-003: Cryptographically Linked Hash-Chained Audit Ledger
- **Status:** Accepted
- **Context:** CERT-In directions mandate maintaining unaltered logs for 180 days. Conventional syslog is vulnerable to truncation or alteration if administrative credentials are compromised.
- **Decision:** Store every administrative and security mutation in a cryptographic append-only hash chain (`SHA-256`), where record $n$ signs the hash of record $n-1$. Any tampering immediately invalidates ledger verification.

### ADR-004: Strict Guardrails and Human Confirmation for Local AI Security Actions
- **Status:** Accepted
- **Context:** Automated AI agents with full shell access risk causing accidental production outages or being manipulated through prompt injection.
- **Decision:** Local AI operates strictly as an advisory and correlation layer. Low-risk operations (e.g. temporary IP rate-limiting with expiry, diagnostics collection) can be policy-automated, but high-impact actions (stopping production containers, blocking subnet, rotating certificates) require explicit human approval. Critical state changes require dual administrative sign-off.
