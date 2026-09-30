# Air-Gapped Operation & Offline Update Procedures
**Appliance Edition:** CSIR-SWA OS Air-Gapped Strategic Edition

---

## 1. Operating Concept
The Strategic Air-Gapped Edition operates in high-security, classified research, or disconnected laboratory environments. It requires zero outbound or inbound Internet access.

## 2. Update Ingestion Protocol
1. **Bundle Packaging (External Secure Cleanroom):**
   - Packages and container images are pulled on a dedicated build server.
   - SBOM generated via Syft in CycloneDX format.
   - Vulnerability scan generated via Grype/Trivy (VEX statement attached).
   - Bundle signed with CSIR Release Engineering Cosign & GPG private keys:
     ```bash
     csir-bundle-pack --channel air-gap --version 1.0.1 --out csir-swa-bundle-1.0.1.tar.gz
     ```
2. **Physical Transfer & Verification:**
   - Transferred via approved read-only optical disc or cryptographically cleared USB media.
   - Target appliance reads bundle into `/srv/repository/incoming/`.
   - The appliance verifies signature against the trusted embedded public key in `/etc/pki/csir/csir-release.pub`.
3. **Execution & Rollback Protection:**
   - Node Agent applies offline RPM updates into a new Btrfs snapshot using `transactional-update --offline`.
   - Podman container images imported into local storage (`/var/lib/containers`).
   - Appliance validates health checks before final promotion.
