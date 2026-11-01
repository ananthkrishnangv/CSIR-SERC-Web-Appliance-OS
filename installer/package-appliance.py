#!/usr/bin/env python3
"""
CSIR-SERC Secure Web Appliance OS - Standalone Installer Package Builder
Packages the complete universal installer into a self-contained .tar.gz archive
with cryptographic SHA-256 verification.
"""

import os
import sys
import tarfile
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTALLER_DIR = BASE_DIR / "installer"
DIST_DIR = INSTALLER_DIR / "dist"
VERSION = "1.0.0"
PACKAGE_NAME = f"csir-appliance-installer-v{VERSION}.tar.gz"

def hash_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1048576):
            h.update(chunk)
    return h.hexdigest()

def package():
    print(f"[*] Packaging CSIR-SERC Appliance Installer v{VERSION}...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    out_tar = DIST_DIR / PACKAGE_NAME

    # Required directories to bundle
    include_paths = [
        ("installer/setup-appliance.sh", "setup-appliance.sh"),
        ("installer/convert-microos.sh", "convert-microos.sh"),
        ("installer/install.sh", "install.sh"),
        ("installer/modules", "modules"),
        ("installer/post-install", "post-install"),
        ("installer/assets", "assets"),
        ("installer/README.md", "README.md"),
        ("backend/app", "backend/app"),
        ("backend/node_agent", "backend/node_agent"),
        ("backend/cli", "backend/cli"),
        ("templates", "templates"),
        ("security-profiles", "security-profiles"),
    ]

    with tarfile.open(out_tar, "w:gz") as tar:
        for src_rel, arc_name in include_paths:
            full_src = BASE_DIR / src_rel
            if full_src.exists():
                print(f"  + Bundling {src_rel} -> {arc_name}")
                tar.add(full_src, arcname=arc_name)
            else:
                print(f"  ! Warning: {src_rel} does not exist, skipping.")

    file_size = out_tar.stat().st_size
    sha256 = hash_file(out_tar)
    sha_file = DIST_DIR / f"{PACKAGE_NAME}.sha256"
    with open(sha_file, "w", encoding="utf-8") as sf:
        sf.write(f"{sha256}  {PACKAGE_NAME}\n")

    print(f"[OK] Package built successfully: {out_tar}")
    print(f"    Size:   {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"    SHA256: {sha256}")
    print(f"[OK] Checksum written to {sha_file}")

if __name__ == "__main__":
    package()
