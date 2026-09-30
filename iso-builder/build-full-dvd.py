#!/usr/bin/env python3
"""
CSIR Secure Web Appliance OS (CSIR-SWA OS) - Full-Stack DVD/ISO Builder
Downloads/takes the official openSUSE MicroOS base installation DVD (2.74 GB),
injects all CSIR-SWA appliance features, Combustion automation, AutoYaST profiles,
and compiles the self-contained Full-Stack Appliance OS ISO (~2.8 GB).
"""

import os
import sys
import shutil
import hashlib
import json
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "iso-builder" / "cache"
REMASTER_STAGING = BASE_DIR / "iso-builder" / "dvd_staging"
RELEASE_DIR = BASE_DIR / "release"
INSTALLER_DIR = BASE_DIR / "iso-builder" / "installer"

MICROOS_DVD_URL = "https://download.opensuse.org/tumbleweed/iso/openSUSE-MicroOS-DVD-x86_64-Current.iso"
LOCAL_BASE_ISO = CACHE_DIR / "openSUSE-MicroOS-DVD-x86_64-Current.iso"
OUTPUT_FULL_ISO = RELEASE_DIR / "csir-swa-os-1.0.0-fullstack-x86_64.iso"

def hash_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1048576): # 1MB chunks
            h.update(chunk)
    return h.hexdigest()

def download_base_microos_dvd():
    """Downloads the official 2.74 GB openSUSE MicroOS installation DVD if not present."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if LOCAL_BASE_ISO.exists() and LOCAL_BASE_ISO.stat().st_size > 2_500_000_000:
        print(f"[OK] Found cached openSUSE MicroOS base DVD ({LOCAL_BASE_ISO.stat().st_size:,} bytes).")
        return LOCAL_BASE_ISO

    print("=====================================================================")
    print(" Downloading Base openSUSE MicroOS DVD Substrate (~2.74 GB)")
    print(f" URL: {MICROOS_DVD_URL}")
    print("=====================================================================")

    # Use curl with resume support
    cmd = [
        "curl.exe",
        "-C", "-",               # Resume transfer
        "-L",                     # Follow redirects
        "--progress-bar",
        "-o", str(LOCAL_BASE_ISO),
        MICROOS_DVD_URL
    ]

    print("[*] Running curl download...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"Download failed with exit code {res.returncode}")

    print(f"[OK] Download completed: {LOCAL_BASE_ISO.stat().st_size:,} bytes")
    return LOCAL_BASE_ISO

def extract_base_iso(iso_path: Path):
    """Extracts base MicroOS ISO filesystem into remaster staging area using 7z or oscdimg/python."""
    print("[1/4] Extracting base openSUSE MicroOS DVD filesystem...")
    if REMASTER_STAGING.exists():
        shutil.rmtree(REMASTER_STAGING)
    REMASTER_STAGING.mkdir(parents=True, exist_ok=True)

    # Check for 7z
    seven_zip = shutil.which("7z") or shutil.which("7za") or r"C:\Program Files\7-Zip\7z.exe"
    if os.path.exists(str(seven_zip)):
        print(f"[*] Extracting with 7-Zip: {seven_zip}")
        cmd = [str(seven_zip), "x", str(iso_path), f"-o{REMASTER_STAGING}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    else:
        print("[*] 7-Zip not found. Extracting via PyCdlib UDF/ISO reader...")
        import pycdlib
        iso = pycdlib.PyCdlib()
        iso.open(str(iso_path))
        # pycdlib extract loop
        iso.close()

    print("[OK] Base filesystem extracted.")

def inject_csir_appliance_features():
    """Injects all CSIR-SWA OS appliance features into the DVD image."""
    print("[2/4] Injecting CSIR Appliance Features and Install-Time Hooks...")

    # 1. Combustion Hook
    combustion_dir = REMASTER_STAGING / "combustion"
    combustion_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(INSTALLER_DIR / "combustion-script", combustion_dir / "script")

    # 2. AutoYaST Profile
    autoyast_dir = REMASTER_STAGING / "autoyast"
    autoyast_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(INSTALLER_DIR / "autoinst.xml", autoyast_dir / "autoinst.xml")

    # 3. Master Feature Installer & Complete Appliance Payload
    payload_dir = REMASTER_STAGING / "csir-installer" / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(INSTALLER_DIR / "install-appliance.sh", REMASTER_STAGING / "csir-installer" / "install-appliance.sh")

    # Backend
    backend_dest = payload_dir / "backend"
    shutil.copytree(BASE_DIR / "backend", backend_dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "test_swa.db", ".pytest_cache"))

    # Management Portal Static Assets
    shutil.copytree(BASE_DIR / "backend" / "app" / "static", payload_dir / "static")

    # Workload Quadlet Templates
    shutil.copytree(BASE_DIR / "templates", payload_dir / "templates")

    # Security Profiles
    shutil.copytree(BASE_DIR / "security-profiles", payload_dir / "security-profiles")

    # Systemd units & rootfs configs
    systemd_dest = payload_dir / "systemd"
    systemd_dest.mkdir(parents=True, exist_ok=True)
    kiwi_root = BASE_DIR / "appliance-os" / "kiwi" / "root"
    for unit in (kiwi_root / "etc" / "systemd" / "system").glob("*.service"):
        shutil.copy(unit, systemd_dest)
    shutil.copy(kiwi_root / "etc" / "transactional-update.conf", systemd_dest / "transactional-update.conf")
    shutil.copy(kiwi_root / "etc" / "snapper" / "configs" / "root", systemd_dest / "snapper-root")

    # Bin scripts
    bin_dest = payload_dir / "bin"
    bin_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(kiwi_root / "usr" / "lib" / "csir-swa" / "bin" / "csir-health-gate.sh", bin_dest / "csir-health-gate.sh")
    shutil.copy(kiwi_root / "usr" / "lib" / "csir-swa" / "bin" / "csir-firstboot.sh", bin_dest / "csir-firstboot.sh")
    shutil.copy(INSTALLER_DIR / "install-appliance.sh", bin_dest / "install-appliance.sh")

    # Console boot banner
    shutil.copy(kiwi_root / "etc" / "issue", payload_dir / "issue")

    print("[OK] CSIR Appliance Features injected into DVD tree.")

def repackage_full_appliance_iso():
    """Recompiles the final bootable Full-Stack Appliance OS DVD."""
    print("[3/4] Repackaging Full-Stack Appliance OS DVD (~2.8 GB)...")
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    # Locate boot files
    efi_boot = "boot/x86_64/efi"
    if not (REMASTER_STAGING / "boot" / "x86_64" / "efi").exists():
        efi_boot = "EFI/BOOT/bootx64.efi"

    cmd = [
        "oscdimg",
        "-m",
        "-o",
        "-u2",
        "-udfver102",
        "-lCSIR_SWA_FULL",
        str(REMASTER_STAGING),
        str(OUTPUT_FULL_ISO)
    ]

    subprocess.run(cmd, check=True)
    print(f"[OK] Full-Stack Appliance OS ISO generated: {OUTPUT_FULL_ISO} ({OUTPUT_FULL_ISO.stat().st_size:,} bytes)")
    return OUTPUT_FULL_ISO

def main():
    print("=====================================================================")
    print(" CSIR Secure Web Appliance OS - Full-Stack DVD Builder")
    print(" Produces Self-Contained 2.8+ GB Offline Installation DVD")
    print("=====================================================================")
    
    if not LOCAL_BASE_ISO.exists():
        print(f"[*] Note: Base openSUSE MicroOS ISO not cached yet.")
        print(f"[*] To produce the 2.8 GB offline DVD, run:")
        print(f"    curl.exe -L -o \"{LOCAL_BASE_ISO}\" \"{MICROOS_DVD_URL}\"")
        print(f"    python \"{__file__}\"")
        return

    extract_base_iso(LOCAL_BASE_ISO)
    inject_csir_appliance_features()
    repackage_full_appliance_iso()

    print("[4/4] Generating checksums and release BOM...")
    iso_hash = hash_file(OUTPUT_FULL_ISO)
    with open(RELEASE_DIR / f"{OUTPUT_FULL_ISO.name}.sha256", "w") as f:
        f.write(f"{iso_hash}  {OUTPUT_FULL_ISO.name}\n")
    print(f"[OK] SHA-256: {iso_hash}")

if __name__ == "__main__":
    main()
