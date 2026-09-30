import datetime
from pydantic import BaseModel, Field

class ApplicationBase(BaseModel):
    name: str = Field(..., example="CSIR Research Portal")
    description: str = Field("", example="National scientific research portal")
    image: str = Field(..., example="registry.csir.res.in/apps/research-portal:1.2.0")
    port: int = Field(..., example=8080)
    domain: str = Field(..., example="research.csir.res.in")
    waf_mode: str = Field("strict", example="strict")

class ApplicationCreate(ApplicationBase):
    cpu_limit: int = Field(50, example=50) # CPU percent
    memory_mb: int = Field(512, example=512)
    env_vars: dict[str, str] = Field(default_factory=dict)
    volumes: list[str] = Field(default_factory=list)

class ApplicationResponse(ApplicationBase):
    id: int
    app_id: str
    digest: str
    status: str
    health: str
    backup_status: str
    cpu_percent: int
    memory_mb: int
    is_rootless: bool
    quadlet_path: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class ApplicationActionRequest(BaseModel):
    action: str = Field(..., example="restart") # start, stop, restart, rollback
