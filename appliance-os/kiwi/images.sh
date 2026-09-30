#!/bin/bash
#======================================
# Post-package installation cleanup & packaging for CSIR-SWA OS
#======================================
set -euxo pipefail

echo "Executing CSIR-SWA OS images.sh image post-processing..."

# 1. Clean zypper caches
zypper clean --all || true
rm -rf /var/cache/zypp/* /tmp/* /var/tmp/*

# 2. Reset machine-id for appliance first-boot generation
truncate -s 0 /etc/machine-id
rm -f /var/lib/dbus/machine-id

# 3. Secure permissions on sensitive directories
chmod 700 /root
chmod 755 /etc

# 4. Generate appliance build stamp and release metadata
mkdir -p /etc/csir-swa
cat <<EOF > /etc/csir-swa/version.json
{
  "product": "CSIR Secure Web Appliance OS",
  "short_name": "CSIR-SWA OS",
  "version": "1.0.0",
  "baseline_date": "2026-09-28",
  "build_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "channel": "Stable",
  "base_os": "openSUSE MicroOS",
  "python_version": "3.14.7",
  "podman_version": "6.1.2",
  "architectures": ["x86_64"],
  "compliance": ["CERT-In", "ISO 27001", "DPDP Act"]
}
EOF

echo "CSIR-SWA OS images.sh completed."
exit 0
