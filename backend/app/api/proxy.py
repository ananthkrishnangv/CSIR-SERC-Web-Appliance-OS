from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/proxy", tags=["Reverse Proxy & Upstreams"])

class UpstreamPoolCreate(BaseModel):
    name: str = Field(..., example="Structural Health Telemetry Pool")
    algorithm: str = Field("Round-Robin", example="Round-Robin")
    path_prefix: str = Field(..., example="/api/v1/shm/*")
    health_uri: str = Field("/healthz", example="/healthz")
    check_interval: int = 5
    targets: List[str] = Field(..., example=["10.20.10.101:8081", "10.20.10.102:8081"])

class UpstreamPoolResponse(BaseModel):
    pool_id: str
    name: str
    algorithm: str
    path_prefix: str
    health_uri: str
    check_interval: int
    active_targets: int
    total_targets: int
    avg_latency: float
    targets: List[str]

_UPSTREAMS_DB = [
    {
        "pool_id": "pool-01",
        "name": "Structural Health Telemetry Pool",
        "algorithm": "Round-Robin",
        "path_prefix": "/api/v1/shm/*",
        "health_uri": "/healthz",
        "check_interval": 5,
        "active_targets": 3,
        "total_targets": 3,
        "avg_latency": 4.2,
        "targets": ["10.20.10.101:8081", "10.20.10.102:8081", "10.20.10.103:8081"]
    },
    {
        "pool_id": "pool-02",
        "name": "Wind Tunnel High-Rate Ingestion",
        "algorithm": "Least-Connections",
        "path_prefix": "/ingest/aerodynamics/*",
        "health_uri": "/api/ping",
        "check_interval": 3,
        "active_targets": 2,
        "total_targets": 2,
        "avg_latency": 2.8,
        "targets": ["10.20.10.201:8082", "10.20.10.202:8082"]
    },
    {
        "pool_id": "pool-03",
        "name": "Sovereign AI Inference & ChatOps",
        "algorithm": "IP-Hash Session Pinned",
        "path_prefix": "/api/v1/ai-security/*",
        "health_uri": "/health",
        "check_interval": 10,
        "active_targets": 2,
        "total_targets": 2,
        "avg_latency": 12.5,
        "targets": ["127.0.0.1:8000", "127.0.0.1:8001"]
    }
]

@router.get("/upstreams", response_model=List[UpstreamPoolResponse])
def list_upstream_pools():
    """
    Returns all HAProxy upstream backend pools and dynamic health telemetry.
    """
    return _UPSTREAMS_DB

@router.post("/upstreams", response_model=UpstreamPoolResponse, status_code=status.HTTP_201_CREATED)
def create_upstream_pool(req: UpstreamPoolCreate):
    new_id = f"pool-{len(_UPSTREAMS_DB) + 1:02d}"
    pool = {
        "pool_id": new_id,
        "name": req.name,
        "algorithm": req.algorithm,
        "path_prefix": req.path_prefix,
        "health_uri": req.health_uri,
        "check_interval": req.check_interval,
        "active_targets": len(req.targets),
        "total_targets": len(req.targets),
        "avg_latency": 3.5,
        "targets": req.targets
    }
    _UPSTREAMS_DB.append(pool)
    return pool

@router.delete("/upstreams/{pool_id}")
def delete_upstream_pool(pool_id: str):
    global _UPSTREAMS_DB
    found = any(p["pool_id"] == pool_id for p in _UPSTREAMS_DB)
    if not found:
        raise HTTPException(status_code=404, detail="Upstream pool not found")
    _UPSTREAMS_DB = [p for p in _UPSTREAMS_DB if p["pool_id"] != pool_id]
    return {"status": "success", "message": f"Upstream pool {pool_id} deleted."}
