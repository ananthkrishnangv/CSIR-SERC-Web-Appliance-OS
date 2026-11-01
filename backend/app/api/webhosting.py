from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/webhosting", tags=["Web Hosting & Virtual Hosts"])

class VirtualHostCreate(BaseModel):
    domain: str = Field(..., example="serc.res.in")
    aliases: Optional[str] = Field("", example="www.serc.res.in, portal.serc.res.in")
    docroot: Optional[str] = Field(None, example="/srv/www/vhosts/serc.res.in/public_html")
    runtime: str = Field("PHP 8.2-FPM", example="PHP 8.2-FPM")
    ssl_enabled: bool = True
    storage_quota_gb: int = 50

class VirtualHostResponse(BaseModel):
    id: str
    domain: str
    aliases: str
    docroot: str
    runtime: str
    runtime_badge: str
    ssl_status: str
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
        "ssl_status": "Let's Encrypt (Auto-Renew)",
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
        "ssl_status": "Wildcard *.serc.res.in",
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
        "ssl_status": "Let's Encrypt (Auto-Renew)",
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
        "ssl_status": "Wildcard *.serc.res.in",
        "storage_used": "22.8 GB",
        "storage_quota": "100 GB",
        "quota_percent": 23
    }
]

@router.get("/vhosts", response_model=List[VirtualHostResponse])
def list_virtual_hosts():
    """
    Returns all registered virtual hosts, runtimes, document roots, and storage quotas.
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
    if "php" in req.runtime.lower():
        badge = "bg-indigo-100 text-indigo-800"
    elif "node" in req.runtime.lower():
        badge = "bg-emerald-100 text-emerald-800"
    elif "python" in req.runtime.lower():
        badge = "bg-sky-100 text-sky-800"

    vhost = {
        "id": new_id,
        "domain": req.domain,
        "aliases": req.aliases or "",
        "docroot": docroot,
        "runtime": req.runtime,
        "runtime_badge": badge,
        "ssl_status": "ACME Provisioning" if req.ssl_enabled else "Disabled",
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
