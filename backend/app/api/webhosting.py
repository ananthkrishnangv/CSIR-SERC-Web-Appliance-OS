from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/webhosting", tags=["Web Hosting & Virtual Hosts"])

class VirtualHostCreate(BaseModel):
    domain: str = Field(..., example="lab.serc.res.in")
    aliases: Optional[str] = Field("", example="www.lab.serc.res.in")
    docroot: Optional[str] = Field(None, example="/srv/www/vhosts/lab.serc.res.in/public_html")
    runtime: str = Field("PHP 8.2-FPM", example="PHP 8.2-FPM")
    install_backend_app: bool = Field(True, description="Automatically install & provision background runtime stack")
    backend_app_type: str = Field("php", example="php")  # php, node, python, static
    backend_app_workers: int = Field(4, ge=1, le=32)
    ssl_enabled: bool = Field(True, description="Enable SSL / TLS certificate encryption")
    ssl_provider: str = Field("letsencrypt", example="letsencrypt")  # letsencrypt, custom, tpm_internal
    ssl_force_https: bool = Field(True, description="HTTP 301 Permanent redirect to HTTPS")
    ssl_hsts: bool = Field(True, description="HTTP Strict Transport Security header")
    storage_quota_gb: int = Field(50, ge=5, le=500)

class VirtualHostResponse(BaseModel):
    id: str
    domain: str
    aliases: str
    docroot: str
    runtime: str
    runtime_badge: str
    app_stack: str
    ssl_status: str
    ssl_provider: str
    force_https: bool
    storage_used: str
    storage_quota: str
    quota_percent: int

# In-memory virtual hosts store pre-seeded with sovereign government research portals
_VHOSTS_DB = [
    {
        "id": "vh-01",
        "domain": "serc.res.in",
        "aliases": "www.serc.res.in, portal.serc.res.in",
        "docroot": "/srv/www/vhosts/serc.res.in/public_html",
        "runtime": "PHP 8.2-FPM",
        "runtime_badge": "bg-indigo-100 text-indigo-800",
        "app_stack": "PHP 8.2-FPM (5 Workers, OPcache, MySQLi, cURL)",
        "ssl_status": "Let's Encrypt (Auto-Renew)",
        "ssl_provider": "letsencrypt",
        "force_https": True,
        "storage_used": "14.2 GB",
        "storage_quota": "50 GB",
        "quota_percent": 28
    },
    {
        "id": "vh-02",
        "domain": "wind.serc.res.in",
        "aliases": "tunnel-data.serc.res.in",
        "docroot": "/srv/www/vhosts/wind.serc.res.in/dist",
        "runtime": "Node.js 20 SSR",
        "runtime_badge": "bg-emerald-100 text-emerald-800",
        "app_stack": "Node.js 20 LTS (pm2 supervisor, port 3000)",
        "ssl_status": "Wildcard *.serc.res.in",
        "ssl_provider": "custom",
        "force_https": True,
        "storage_used": "8.5 GB",
        "storage_quota": "30 GB",
        "quota_percent": 28
    },
    {
        "id": "vh-03",
        "domain": "sensors.serc.res.in",
        "aliases": "telemetry.serc.res.in",
        "docroot": "/srv/www/vhosts/sensors.serc.res.in/app",
        "runtime": "Python ASGI / FastHTML",
        "runtime_badge": "bg-sky-100 text-sky-800",
        "app_stack": "Python 3.11 ASGI (Uvicorn 4 workers, venv isolated)",
        "ssl_status": "Let's Encrypt (Auto-Renew)",
        "ssl_provider": "letsencrypt",
        "force_https": True,
        "storage_used": "4.1 GB",
        "storage_quota": "20 GB",
        "quota_percent": 20
    },
    {
        "id": "vh-04",
        "domain": "archive.serc.res.in",
        "aliases": "open-access.serc.res.in",
        "docroot": "/srv/www/vhosts/archive.serc.res.in/htdocs",
        "runtime": "Static / Nginx Fast-Cache",
        "runtime_badge": "bg-slate-100 text-slate-800",
        "app_stack": "Static / Brotli Pre-Compressed Assets",
        "ssl_status": "Wildcard *.serc.res.in",
        "ssl_provider": "custom",
        "force_https": True,
        "storage_used": "22.8 GB",
        "storage_quota": "100 GB",
        "quota_percent": 23
    }
]

@router.get("/vhosts", response_model=List[VirtualHostResponse])
def list_virtual_hosts():
    """
    Returns all registered virtual hosts, runtimes, background applications, and SSL configs.
    """
    return _VHOSTS_DB

@router.post("/vhosts", response_model=VirtualHostResponse, status_code=status.HTTP_201_CREATED)
def create_virtual_host(req: VirtualHostCreate):
    for vh in _VHOSTS_DB:
        if vh["domain"].lower() == req.domain.lower():
            raise HTTPException(status_code=400, detail=f"Virtual host {req.domain} already exists.")

    new_id = f"vh-{len(_VHOSTS_DB) + 1:02d}"
    docroot = req.docroot or f"/srv/www/vhosts/{req.domain}/public_html"
    
    badge = "bg-slate-100 text-slate-800"
    app_desc = "Static Assets"
    if "php" in req.runtime.lower():
        badge = "bg-indigo-100 text-indigo-800"
        app_desc = f"PHP 8.2-FPM ({req.backend_app_workers} Workers, OPcache)"
    elif "node" in req.runtime.lower():
        badge = "bg-emerald-100 text-emerald-800"
        app_desc = f"Node.js 20 LTS (pm2 process manager)"
    elif "python" in req.runtime.lower():
        badge = "bg-sky-100 text-sky-800"
        app_desc = f"Python 3.11 ASGI (Uvicorn {req.backend_app_workers} workers)"

    if req.ssl_enabled:
        if req.ssl_provider == "letsencrypt":
            ssl_label = "Let's Encrypt (Auto-Renew)"
        elif req.ssl_provider == "tpm_internal":
            ssl_label = "TPM Hardware CA Signed"
        else:
            ssl_label = "Custom Certificate Installed"
    else:
        ssl_label = "Disabled (HTTP Only)"

    vhost = {
        "id": new_id,
        "domain": req.domain,
        "aliases": req.aliases or "",
        "docroot": docroot,
        "runtime": req.runtime,
        "runtime_badge": badge,
        "app_stack": app_desc if req.install_backend_app else "Unmanaged Runtime",
        "ssl_status": ssl_label,
        "ssl_provider": req.ssl_provider,
        "force_https": req.ssl_force_https,
        "storage_used": "0.1 GB",
        "storage_quota": f"{req.storage_quota_gb} GB",
        "quota_percent": 1
    }
    _VHOSTS_DB.append(vhost)
    return vhost

@router.delete("/vhosts/{vhost_id}")
def delete_virtual_host(vhost_id: str):
    global _VHOSTS_DB
    found = any(v["id"] == vhost_id for v in _VHOSTS_DB)
    if not found:
        raise HTTPException(status_code=404, detail="Virtual host not found")
    _VHOSTS_DB = [v for v in _VHOSTS_DB if v["id"] != vhost_id]
    return {"status": "success", "message": f"Virtual host {vhost_id} decommissioned."}
