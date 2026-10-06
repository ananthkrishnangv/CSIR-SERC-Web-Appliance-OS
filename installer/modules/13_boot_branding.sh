#!/usr/bin/env bash
#=============================================================================
# CSIR-SERC Secure Web Appliance OS - Module 13: Bootloader & Visual Branding
# Replaces OS bootloader splash, GRUB2 theme & Plymouth with CSIR-SERC Branding
#=============================================================================
set -euo pipefail

apply_bootloader_branding() {
    echo -e "${CYAN}[*] Installing CSIR-SERC Secure Web Appliance OS Boot Splash & GRUB Theme...${NC}"

    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # 1. Determine GRUB configuration paths
    local GRUB_DIR="/boot/grub2"
    local THEME_DIR="/boot/grub2/themes/csir-serc"
    if [ ! -d "/boot/grub2" ] && [ -d "/boot/grub" ]; then
        GRUB_DIR="/boot/grub"
        THEME_DIR="/boot/grub/themes/csir-serc"
    fi

    mkdir -p "$THEME_DIR"

    # 2. Deploy CSIR-SERC GRUB Theme and Visual Assets
    echo -e "    • Deploying theme assets to ${THEME_DIR}..."
    if [ -f "$SCRIPT_DIR/assets/branding/background.jpg" ]; then
        cp "$SCRIPT_DIR/assets/branding/background.jpg" "$THEME_DIR/background.jpg"
    fi
    if [ -f "$SCRIPT_DIR/assets/branding/logo.png" ]; then
        cp "$SCRIPT_DIR/assets/branding/logo.png" "$THEME_DIR/logo.png"
    fi
    if [ -f "$SCRIPT_DIR/assets/branding/grub-theme.txt" ]; then
        cp "$SCRIPT_DIR/assets/branding/grub-theme.txt" "$THEME_DIR/theme.txt"
    fi

    # 3. Update /etc/default/grub
    if [ -f /etc/default/grub ]; then
        echo -e "    • Configuring /etc/default/grub with CSIR-SERC theme..."
        local GRUB_CONF="/etc/default/grub"
        
        # Backup original grub default
        cp "$GRUB_CONF" "${GRUB_CONF}.bak-csir" 2>/dev/null || true

        # Clean existing theme and distributor lines
        sed -i '/^GRUB_THEME=/d' "$GRUB_CONF"
        sed -i '/^GRUB_BACKGROUND=/d' "$GRUB_CONF"
        sed -i '/^GRUB_DISTRIBUTOR=/d' "$GRUB_CONF"

        # Inject CSIR-SERC boot configuration
        cat <<EOF >> "$GRUB_CONF"
GRUB_DISTRIBUTOR="CSIR-SERC Secure Web Appliance OS"
GRUB_THEME="${THEME_DIR}/theme.txt"
GRUB_BACKGROUND="${THEME_DIR}/background.jpg"
GRUB_TIMEOUT=8
EOF

        # 4. Regenerate GRUB Configuration
        echo -e "    • Recompiling bootloader configuration..."
        if command -v grub2-mkconfig >/dev/null 2>&1; then
            local TARGET_CFG="${GRUB_DIR}/grub.cfg"
            if [ -d /sys/firmware/efi ]; then
                # Check for EFI grub location
                for efi_cfg in /boot/efi/EFI/*/grub.cfg; do
                    if [ -f "$efi_cfg" ]; then
                        TARGET_CFG="$efi_cfg"
                        break
                    fi
                done
            fi
            grub2-mkconfig -o "$TARGET_CFG" || grub2-mkconfig -o "${GRUB_DIR}/grub.cfg" || true
        elif command -v update-grub >/dev/null 2>&1; then
            update-grub || true
        fi
    fi

    # 5. Plymouth Bootsplash Integration (if Plymouth installed)
    if command -v plymouth-set-default-theme >/dev/null 2>&1; then
        echo -e "    • Updating Plymouth bootsplash theme..."
        local PLYMOUTH_THEMES="/usr/share/plymouth/themes/csir-serc"
        mkdir -p "$PLYMOUTH_THEMES"
        if [ -f "$SCRIPT_DIR/assets/branding/background.jpg" ]; then
            cp "$SCRIPT_DIR/assets/branding/background.jpg" "$PLYMOUTH_THEMES/background.jpg"
        fi
        if [ -f "$SCRIPT_DIR/assets/branding/logo.png" ]; then
            cp "$SCRIPT_DIR/assets/branding/logo.png" "$PLYMOUTH_THEMES/logo.png"
        fi
    fi

    echo -e "${GREEN}[✓] Bootloader and boot image successfully branded to CSIR-SERC Web Appliance OS.${NC}"
}
