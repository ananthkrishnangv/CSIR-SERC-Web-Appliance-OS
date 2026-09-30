#!/bin/bash
#======================================
# Functions and setup for CSIR-SWA OS
#======================================
set -euxo pipefail

echo "=========================================================="
echo "Configuring CSIR Secure Web Appliance OS image foundation"
echo "=========================================================="

# 1. Base System Hardening
umask 027
sed -i 's/^UMASK.*/UMASK 027/' /etc/login.defs

# 2. Setup Appliance System Accounts
# Dedicated non-login service accounts
useradd -r -s /sbin/nologin -d /var/lib/csir-swa -m -c "CSIR SWA Management" csir-swa || true
useradd -r -s /sbin/nologin -d /srv/apps -m -c "CSIR Rootless Apps" csir-app || true

# Setup subuid and subgid for rootless podman for csir-app
echo "csir-app:100000:65536" >> /etc/subuid
echo "csir-app:100000:65536" >> /etc/subgid

# 3. MicroOS Filesystem & Read-Only Configuration
mkdir -p /srv/apps /srv/app-data /srv/backups /srv/repository /srv/models /var/lib/csir-swa /var/log/audit
chmod 750 /srv/apps /srv/app-data /srv/backups /srv/models /var/lib/csir-swa

# 4. Enable Critical Systemd Services & Timers
systemctl enable transactional-update.timer
systemctl enable snapper-timeline.timer
systemctl enable snapper-cleanup.timer
systemctl enable chronyd.service
systemctl enable nftables.service
systemctl enable sshd.service

# Appliance Services
systemctl enable csir-node-agent.service
systemctl enable csir-control-plane.service
systemctl enable csir-health-gate.service

# 5. Snapper Root Configuration
snapper -c root create-config / || true
sed -i 's/^TIMELINE_MIN_AGE=.*/TIMELINE_MIN_AGE="1800"/' /etc/snapper/configs/root || true
sed -i 's/^TIMELINE_LIMIT_HOURLY=.*/TIMELINE_LIMIT_HOURLY="12"/' /etc/snapper/configs/root || true
sed -i 's/^TIMELINE_LIMIT_DAILY=.*/TIMELINE_LIMIT_DAILY="7"/' /etc/snapper/configs/root || true

# 6. NTP / Timesync Setup (CERT-In mandate: Indian NPL / NIC sources)
cat <<EOF > /etc/chrony.conf
server time.nplindia.org iburst
server ntp.nic.in iburst
server pool.ntp.org iburst
driftfile /var/lib/chrony/drift
makestep 1.0 3
rtcsync
logdir /var/log/chrony
EOF

echo "CSIR-SWA OS KIWI config.sh execution complete."
exit 0
