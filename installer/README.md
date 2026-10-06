# CSIR-SERC Secure Web Appliance OS - Universal Conversion Installer
### Transform Any Existing Linux Installation into a Hardened Institutional Web Appliance

This package allows converting an already deployed physical server or virtual machine running **openSUSE MicroOS**, **openSUSE Leap / Tumbleweed**, **Rocky Linux 8/9/10**, **AlmaLinux 8/9/10**, or **Fedora Linux** into a fully configured, hardened **CSIR-SERC Secure Web Appliance**.

---

## 1. Quick Start

### Method A: One-Line Remote Bootstrap (Online)
```bash
curl -sSL https://raw.githubusercontent.com/ananthkrishnangv/CSIR-SERC-Web-Appliance-OS/main/installer/install.sh | sudo bash
```

### Method B: Standalone Package (Offline / Air-Gapped)
1. Download or transfer `csir-appliance-installer-v1.0.0.tar.gz` to the target server.
2. Extract the archive:
   ```bash
   tar -xzf csir-appliance-installer-v1.0.0.tar.gz
   cd csir-appliance-installer
   ```
3. Run the interactive wizard:
   ```bash
   sudo ./setup-appliance.sh
   ```

---

## 2. Installation Options & Predefined Profiles

| Flag / Option | Description |
|---|---|
| *(No args)* | **Interactive Wizard Mode:** Graphical/Text prompt to select deployment profile or individual components. |
| `--all` / `-a` | Installs all 12 platform subsystems (Monolithic Full Stack). |
| `--unattended` / `-y` | Non-interactive mode for automated cloud-init / post-install provisioning. |
| `--profile full` | All services (Portal, WAF, HAProxy, Podman, PostgreSQL, Snapper/Restic, AI, Boot Branding). |
| `--profile edge-waf` | Edge reverse proxy, Coraza WAF (OWASP CRS v4), nftables, Suricata, and hardening. |
| `--profile app-host` | Podman container quadlets, PostgreSQL 17, reverse proxy, backups, and hardening. |
| `--profile minimal` | Core Management plane, Node Agent RPC, nftables firewall, and system hardening. |
| `--services 1,2,3,4...` | Comma-separated list of individual service IDs to install. |

### Example Unattended Commands
```bash
# Automated full-stack conversion:
sudo ./setup-appliance.sh --unattended --all

# Deploy as an Edge WAF reverse proxy:
sudo ./setup-appliance.sh --unattended --profile edge-waf
```

---

## 3. What the Installer Does

1. **Operating System Detection:**
   - Detects distro family (`suse`, `rhel`, `fedora`, `debian`), package manager (`zypper`, `dnf`, `apt`, `transactional-update`), architecture, and hardware resources.
2. **Conflict Resolution & Pre-Install Cleanup:**
   - Detects and cleanly shuts down conflicting web servers (Apache/httpd, lighttpd, caddy) occupying ports 80/443.
   - Disables conflicting `firewalld` or `ufw` so `nftables` default-deny can manage host security natively.
   - Backs up pre-existing configurations to `/var/backups/csir-preinstall-<timestamp>/`.
3. **Repository Integration:**
   - Dynamically adds production & 3rd party repos for the latest versions of PostgreSQL 17, Podman, HAProxy, Grafana, Prometheus, and security tools.
4. **Service Deployment & Configuration:**
   - Deploys Python 3 FastAPI control plane and privileged Node Agent (`/run/csir-swa/agent.sock`).
   - Deploys UX4G Management Web Console into `/var/lib/csir-swa/static/`.
   - Generates TLS 1.3 certificates and configures HAProxy 3.0 reverse proxy on ports 80, 443, and 8443.
   - Deploys Coraza WAF with OWASP Core Rule Set (CRS) v4 ruleset in `/etc/coraza/`.
   - Applies nftables default-deny ruleset in `/etc/nftables/csir-firewall.nft`.
   - Configures rootless Podman user namespaces (`csir-app:100000:65536`) and certified Quadlets in `/etc/containers/systemd/`.
   - Initializes PostgreSQL 17 with SCRAM-SHA-256 credentials.
   - Configures Btrfs Snapper timeline snapshots and Restic encrypted backups with automated DR drill scripts.
5. **System Hardening & Compliance:**
   - Applies kernel sysctl security baseline in `/etc/sysctl.d/99-csir-security.conf` (ASLR, SYN cookies, reverse path filtering, BPF JIT hardening).
   - Configures security limits in `/etc/security/limits.d/99-csir.conf`.
   - Hardens SSH daemon configuration in `/etc/ssh/sshd_config.d/99-csir-hardening.conf`.
   - Synchronizes time with National Physical Laboratory (NPL) India atomic clocks for CERT-In compliance.
   - Replaces console login banners with institutional CSIR-SERC notices in `/etc/issue` and `/etc/motd`.
6. **Bootloader & Boot Image Customization:**
   - Installs official CSIR-SERC high-resolution GRUB2 theme in `/boot/grub2/themes/csir-serc/`.
   - Updates `/etc/default/grub` and recompiles GRUB configuration so next reboot displays the official CSIR-SERC boot splash.
7. **Audit Stamping:**
   - Records genesis entry in the SHA-256 hash-chained cryptographic ledger at `/var/log/audit/csir_audit.ledger`.
   - Generates `/etc/csir-swa/installation-receipt.json`.

---

## 4. Default Access Credentials

- **Management Web Console:** `https://<APPLIANCE_IP>:8443/` *(or https://localhost:8443/)*
- **REST Control Plane Docs:** `http://<APPLIANCE_IP>:8000/docs`
- **Default Super Admin:** `admin` *(or `admin@csir.res.in`)*
- **Default Password:** `CsirWebOS@2026!`
- **Default MFA TOTP Token:** `123456`
- **Unified Appliance CLI:** `csir-ctl status`
