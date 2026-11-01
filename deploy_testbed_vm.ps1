# ==============================================================================
# CSIR SECURE WEB APPLIANCE OS (CSIR-SWA OS)
# VirtualBox Automated Testbed VM Provisioning & Deployment Script
# ==============================================================================
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\deploy_testbed_vm.ps1 [-Mode <gui|headless>]
#
# Requirements:
#   - VirtualBox 7.x installed (defaults checked in D:\Program Files\Oracle\VirtualBox
#     and C:\Program Files\Oracle\VirtualBox)
#   - Administrator privileges required if VirtualBox kernel drivers (vboxsup)
#     or COM classes need to be registered.
# ==============================================================================

param(
    [ValidateSet("gui", "headless", "screenshot", "stop", "status")]
    [string]$Mode = "gui",

    [int]$MemoryMB = 4096,
    [int]$CpuCount = 2,
    [int]$DiskSizeMB = 30720,  # 30 GB
    [string]$VmName = "CSIR-SWA-OS-TestBed"
)

$ErrorActionPreference = "Stop"

# 1. Resolve Workspace & Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$IsoPath = Join-Path $ScriptDir "release\csir-swa-os-1.0.0-fullstack-x86_64.iso"
$DiskDir = Join-Path $ScriptDir "iso-builder"
$DiskPath = Join-Path $DiskDir "csir-swa-os-disk.vdi"
$ScreenshotPath = Join-Path $ScriptDir "docs\screenshots\testbed_vm_console.png"

# 2. Locate VirtualBox Binaries
$VBoxDir = $null
$CandidatePaths = @(
    "D:\Program Files\Oracle\VirtualBox",
    "C:\Program Files\Oracle\VirtualBox",
    "${env:ProgramFiles}\Oracle\VirtualBox"
)

foreach ($path in $CandidatePaths) {
    if (Test-Path (Join-Path $path "VBoxManage.exe")) {
        $VBoxDir = $path
        break
    }
}

if (-not $VBoxDir) {
    Write-Error "Oracle VirtualBox installation not found in candidate paths. Please ensure VirtualBox is installed."
    exit 1
}

$VBoxManage = Join-Path $VBoxDir "VBoxManage.exe"
$VBoxSVC = Join-Path $VBoxDir "VBoxSVC.exe"
Write-Host "[+] VirtualBox located at: $VBoxDir" -ForegroundColor Cyan

# 3. Check Administrator Privileges and Register COM / Drivers if needed
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($IsAdmin) {
    Write-Host "[+] Running with Administrator privileges. Verifying kernel drivers and COM registration..." -ForegroundColor Green
    
    # Check driver service
    $vboxsupService = Get-Service -Name "vboxsup" -ErrorAction SilentlyContinue
    if (-not $vboxsupService) {
        $DriverPath = Join-Path $VBoxDir "drivers\vboxsup\VBoxSup.sys"
        if (Test-Path $DriverPath) {
            Write-Host "    -> Registering vboxsup kernel service..." -ForegroundColor Yellow
            & sc.exe create vboxsup type= kernel binPath= "`"$DriverPath`"" | Out-Null
        }
    }
    
    # Start driver if stopped
    $vboxsupService = Get-Service -Name "vboxsup" -ErrorAction SilentlyContinue
    if ($vboxsupService -and $vboxsupService.Status -ne "Running") {
        Write-Host "    -> Starting vboxsup service..." -ForegroundColor Yellow
        & sc.exe start vboxsup | Out-Null
    }

    # Register COM Server
    Write-Host "    -> Re-registering VirtualBox COM Server..." -ForegroundColor Yellow
    & "$VBoxSVC" /ReRegServer | Out-Null
    & regsvr32.exe /s (Join-Path $VBoxDir "VBoxProxyStub.dll") | Out-Null
    & regsvr32.exe /s (Join-Path $VBoxDir "VBoxC.dll") | Out-Null
} else {
    Write-Host "[!] Note: Running as standard user. If VBoxManage throws REGDB_E_CLASSNOTREG, please right-click and 'Run as Administrator'." -ForegroundColor DarkYellow
}

# 4. Handle Subcommands
if ($Mode -eq "stop") {
    Write-Host "[*] Powering off $VmName..." -ForegroundColor Yellow
    & "$VBoxManage" controlvm "$VmName" poweroff
    exit 0
}

if ($Mode -eq "status") {
    & "$VBoxManage" showvminfo "$VmName"
    exit 0
}

if ($Mode -eq "screenshot") {
    New-Item -ItemType Directory -Path (Split-Path -Parent $ScreenshotPath) -Force | Out-Null
    Write-Host "[*] Capturing VM console screenshot to: $ScreenshotPath" -ForegroundColor Cyan
    & "$VBoxManage" controlvm "$VmName" screenshotpng "$ScreenshotPath"
    Write-Host "[+] Screenshot saved successfully." -ForegroundColor Green
    exit 0
}

# 5. Check if VM Already Exists
$VmExists = $false
try {
    $Vms = & "$VBoxManage" list vms
    if ($Vms -match "`"$VmName`"") {
        $VmExists = $true
        Write-Host "[+] VM '$VmName' already exists." -ForegroundColor Green
    }
} catch {
    Write-Host "[!] Could not query VMs: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Provision VM if Not Present
if (-not $VmExists) {
    Write-Host "[*] Provisioning new VM: $VmName" -ForegroundColor Cyan
    Write-Host "    - RAM: $MemoryMB MB"
    Write-Host "    - CPUs: $CpuCount"
    Write-Host "    - Disk: $DiskSizeMB MB (30 GB VDI)"
    Write-Host "    - Network: NAT with Port Forwarding (8443->443, 8080->80, 2222->22, 8000->8000)"

    if (-not (Test-Path $IsoPath)) {
        Write-Error "Fullstack ISO not found at: $IsoPath. Run release builder first."
        exit 1
    }

    # Create VM definition
    & "$VBoxManage" createvm --name "$VmName" --ostype "OpenSUSE_64" --register

    # System parameters
    & "$VBoxManage" modifyvm "$VmName" --cpus $CpuCount --memory $MemoryMB --vram 128 --graphicscontroller vmsvga --boot1 dvd --boot2 disk --boot3 none

    # Port forwardings for Management Console, Ingress, and Bastion SSH
    & "$VBoxManage" modifyvm "$VmName" --nic1 nat `
        --natpf1 "https,tcp,,8443,,443" `
        --natpf1 "http,tcp,,8080,,80" `
        --natpf1 "ssh,tcp,,2222,,22" `
        --natpf1 "api,tcp,,8000,,8000"

    # Create 30GB Hard Disk if not present
    if (-not (Test-Path $DiskPath)) {
        Write-Host "[*] Creating 30 GB VDI virtual hard disk at: $DiskPath" -ForegroundColor Cyan
        & "$VBoxManage" createmedium disk --filename "$DiskPath" --size $DiskSizeMB --format VDI
    }

    # Attach SATA Storage Controller
    & "$VBoxManage" storagectl "$VmName" --name "SATA Controller" --add sata --controller IntelAhci --portcount 2

    # Attach Disk (Port 0) and DVD ISO (Port 1)
    & "$VBoxManage" storageattach "$VmName" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "$DiskPath"
    & "$VBoxManage" storageattach "$VmName" --storagectl "SATA Controller" --port 1 --device 0 --type dvddrive --medium "$IsoPath"

    Write-Host "[SUCCESS] VM '$VmName' provisioned and configured successfully!" -ForegroundColor Green
}

# 7. Start the Virtual Machine
Write-Host "[*] Starting VM '$VmName' in mode: $Mode..." -ForegroundColor Cyan

if ($Mode -eq "gui") {
    Write-Host "    -> Launching VirtualBox Interactive Graphical Console..." -ForegroundColor Green
    & "$VBoxManage" startvm "$VmName" --type gui
} elseif ($Mode -eq "headless") {
    Write-Host "    -> Launching in Background Headless Mode..." -ForegroundColor Green
    & "$VBoxManage" startvm "$VmName" --type headless
}

Write-Host "`n==============================================================================" -ForegroundColor Green
Write-Host " CSIR SECURE WEB APPLIANCE TESTBED RUNNING" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " Management Console: https://localhost:8443 (or https://127.0.0.1:8443)"
Write-Host " Ingress HTTP:       http://localhost:8080"
Write-Host " Admin Bastion SSH:  ssh -p 2222 root@localhost"
Write-Host " REST API Docs:      http://localhost:8000/docs"
Write-Host ""
Write-Host " Helper Commands:"
Write-Host "   Capture Screenshot: .\deploy_testbed_vm.ps1 -Mode screenshot"
Write-Host "   Check VM Info:      .\deploy_testbed_vm.ps1 -Mode status"
Write-Host "   Power Off VM:       .\deploy_testbed_vm.ps1 -Mode stop"
Write-Host "==============================================================================`n"
