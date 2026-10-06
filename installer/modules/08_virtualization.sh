#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 08: Virtualization Subsystem
# Configures KVM, QEMU and libvirt hypervisor stack for isolated VM workloads
#=============================================================================
set -euo pipefail

install_virtualization_subsystem() {
    echo -e "${CYAN}[*] Installing Virtualization Subsystem (KVM, QEMU, libvirt)...${NC}"

    case "$DISTRO_FAMILY" in
        "suse")
            zypper install -y patterns-server-kvm_server libvirt qemu-kvm virt-install || zypper install -y libvirt qemu-kvm virt-install || true
            ;;
        "rhel"|"fedora")
            dnf install -y qemu-kvm libvirt libvirt-client virt-install || true
            ;;
        "debian")
            apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients virtinst || true
            ;;
    esac

    # Ensure libvirt socket and daemon are active
    systemctl daemon-reload
    systemctl enable libvirtd || systemctl enable virtqemud || true
    systemctl restart libvirtd || systemctl restart virtqemud || true

    echo -e "${GREEN}[✓] KVM / libvirt Virtualization Subsystem ready.${NC}"
}
