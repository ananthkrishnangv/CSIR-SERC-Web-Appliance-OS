from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/virtualization", tags=["KVM Hypervisor & Virtual Machine Manager"])

class KVMStatusResponse(BaseModel):
    is_installed: bool
    service_status: str
    kvm_module_loaded: bool
    hardware_virtualization_supported: bool
    qemu_version: str
    libvirt_version: str
    active_vms: int
    total_vms: int
    allocated_vcpus: int
    total_host_vcpus: int
    allocated_memory_gb: float
    total_host_memory_gb: float
    storage_pool_path: str
    storage_pool_used_gb: float
    storage_pool_total_gb: float
    virtual_bridge: str
    virtual_network_subnet: str

class VMInstance(BaseModel):
    id: str
    name: str
    description: str
    os_distro: str
    state: str  # running, shut off, paused
    vcpus: int
    memory_mb: int
    disk_size_gb: int
    ip_address: str
    uptime: str
    vnc_port: int
    autostart: bool
    created_at: str

class VMCreateRequest(BaseModel):
    name: str = Field(..., example="vm-serc-fem-01")
    description: Optional[str] = Field("", example="Structural Finite Element Simulation")
    os_distro: str = Field("openSUSE Leap 15.6", example="openSUSE Leap 15.6")
    vcpus: int = Field(4, ge=1, le=64)
    memory_mb: int = Field(8192, ge=512, le=262144)
    disk_size_gb: int = Field(100, ge=10, le=2048)
    autostart: bool = True

class VMActionRequest(BaseModel):
    action: str = Field(..., example="start")  # start, stop, restart, pause, resume

# In-memory hypervisor state
_KVM_STATE = {
    "is_installed": True,
    "service_status": "active (running)",
    "kvm_module_loaded": True,
    "hardware_virtualization_supported": True,
    "qemu_version": "QEMU 8.2.1 (openSUSE MicroOS Package)",
    "libvirt_version": "libvirt 9.9.0 (VirtIO & SPICE Enabled)",
    "total_host_vcpus": 16,
    "total_host_memory_gb": 32.0,
    "storage_pool_path": "/var/lib/libvirt/images",
    "storage_pool_used_gb": 360.0,
    "storage_pool_total_gb": 1000.0,
    "virtual_bridge": "virbr0",
    "virtual_network_subnet": "192.168.122.0/24"
}

_VMS_DB = [
    {
        "id": "vm-01",
        "name": "vm-serc-lab-fem",
        "description": "CSIR-SERC Structural Analysis & Finite Element Engine",
        "os_distro": "openSUSE Leap 15.6 (Hardened Server)",
        "state": "running",
        "vcpus": 4,
        "memory_mb": 8192,
        "disk_size_gb": 100,
        "ip_address": "192.168.122.42",
        "uptime": "14 days, 6 hours",
        "vnc_port": 5901,
        "autostart": True,
        "created_at": "2026-10-14T08:00:00Z"
    },
    {
        "id": "vm-02",
        "name": "vm-telemetry-cluster",
        "description": "PostgreSQL 16 High-Availability Sensor Cluster",
        "os_distro": "openSUSE MicroOS Container Host",
        "state": "running",
        "vcpus": 4,
        "memory_mb": 8192,
        "disk_size_gb": 150,
        "ip_address": "192.168.122.88",
        "uptime": "21 days, 11 hours",
        "vnc_port": 5902,
        "autostart": True,
        "created_at": "2026-10-10T12:00:00Z"
    },
    {
        "id": "vm-03",
        "name": "vm-wind-tunnel-sim",
        "description": "Aerodynamic Telemetry Computational Fluid Dynamics",
        "os_distro": "Ubuntu 24.04 LTS (HPC Optimized)",
        "state": "running",
        "vcpus": 4,
        "memory_mb": 8192,
        "disk_size_gb": 70,
        "ip_address": "192.168.122.105",
        "uptime": "3 days, 18 hours",
        "vnc_port": 5903,
        "autostart": True,
        "created_at": "2026-10-28T09:30:00Z"
    },
    {
        "id": "vm-04",
        "name": "vm-legacy-ftp-gateway",
        "description": "Departmental Archival FTP & Legacy RPC Interop Gateway",
        "os_distro": "Debian 12 Bookworm (Minimal Air-Gapped)",
        "state": "shut off",
        "vcpus": 2,
        "memory_mb": 4096,
        "disk_size_gb": 40,
        "ip_address": "192.168.122.210",
        "uptime": "Offline",
        "vnc_port": 5904,
        "autostart": False,
        "created_at": "2026-10-01T14:15:00Z"
    }
]

@router.get("/kvm/status", response_model=KVMStatusResponse)
def get_kvm_status():
    """
    Returns KVM Hypervisor operational status, CPU virtualization support, and resource limits.
    """
    active_count = sum(1 for v in _VMS_DB if v["state"] == "running")
    alloc_vcpus = sum(v["vcpus"] for v in _VMS_DB if v["state"] == "running")
    alloc_mem = sum(v["memory_mb"] for v in _VMS_DB if v["state"] == "running") / 1024.0

    return {
        **_KVM_STATE,
        "active_vms": active_count,
        "total_vms": len(_VMS_DB),
        "allocated_vcpus": alloc_vcpus,
        "allocated_memory_gb": round(alloc_mem, 1)
    }

@router.post("/kvm/install")
def install_kvm_subsystem():
    """
    Installs and initializes KVM, libvirtd, qemu-kvm, virt-install, and cockpit-machines.
    """
    _KVM_STATE["is_installed"] = True
    _KVM_STATE["service_status"] = "active (running)"
    _KVM_STATE["kvm_module_loaded"] = True
    return {
        "status": "success",
        "message": "KVM Hypervisor, Libvirt Daemon, and Virtual Machine Manager installed and initialized successfully.",
        "packages": [
            "qemu-kvm",
            "libvirt-daemon-system",
            "libvirt-clients",
            "virt-install",
            "cockpit-machines",
            "bridge-utils"
        ]
    }

@router.post("/kvm/toggle-mode")
def toggle_kvm_installed_mode():
    """
    Toggles between installed and not-installed mode for testing and screenshot verification.
    """
    _KVM_STATE["is_installed"] = not _KVM_STATE["is_installed"]
    return {
        "is_installed": _KVM_STATE["is_installed"],
        "message": f"KVM status switched to {'Installed' if _KVM_STATE['is_installed'] else 'Uninstalled'}"
    }

@router.get("/kvm/vms", response_model=List[VMInstance])
def list_virtual_machines():
    """
    Returns all configured KVM virtual machines with real-time state, vCPUs, RAM, and IP.
    """
    if not _KVM_STATE["is_installed"]:
        return []
    return _VMS_DB

@router.post("/kvm/vms", response_model=VMInstance, status_code=status.HTTP_201_CREATED)
def create_virtual_machine(req: VMCreateRequest):
    if not _KVM_STATE["is_installed"]:
        raise HTTPException(status_code=400, detail="KVM Hypervisor is not installed. Please initialize KVM first.")

    new_id = f"vm-{len(_VMS_DB) + 1:02d}"
    vnc_port = 5900 + len(_VMS_DB) + 1
    ip_last = 100 + len(_VMS_DB) + 1

    new_vm = {
        "id": new_id,
        "name": req.name,
        "description": req.description or f"{req.os_distro} Instance",
        "os_distro": req.os_distro,
        "state": "running",
        "vcpus": req.vcpus,
        "memory_mb": req.memory_mb,
        "disk_size_gb": req.disk_size_gb,
        "ip_address": f"192.168.122.{ip_last}",
        "uptime": "Just Started",
        "vnc_port": vnc_port,
        "autostart": req.autostart,
        "created_at": "2026-11-02T02:00:00Z"
    }
    _VMS_DB.append(new_vm)
    return new_vm

@router.post("/kvm/vms/{vm_id}/action")
def control_virtual_machine(vm_id: str, req: VMActionRequest):
    vm = next((v for v in _VMS_DB if v["id"] == vm_id), None)
    if not vm:
        raise HTTPException(status_code=404, detail="Virtual machine not found")

    act = req.action.lower()
    if act == "start":
        vm["state"] = "running"
        vm["uptime"] = "0m"
    elif act in ["stop", "shutdown"]:
        vm["state"] = "shut off"
        vm["uptime"] = "Offline"
    elif act == "restart":
        vm["state"] = "running"
        vm["uptime"] = "0m"
    elif act == "pause":
        vm["state"] = "paused"
    elif act == "resume":
        vm["state"] = "running"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {req.action}")

    return {"status": "success", "vm_id": vm_id, "new_state": vm["state"]}

@router.delete("/kvm/vms/{vm_id}")
def delete_virtual_machine(vm_id: str):
    global _VMS_DB
    found = any(v["id"] == vm_id for v in _VMS_DB)
    if not found:
        raise HTTPException(status_code=404, detail="Virtual machine not found")
    _VMS_DB = [v for v in _VMS_DB if v["id"] != vm_id]
    return {"status": "success", "message": f"Virtual machine {vm_id} deleted and QCOW2 storage released."}
