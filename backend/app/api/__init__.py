from app.api.overview import router as overview_router
from app.api.applications import router as applications_router
from app.api.webhosting import router as webhosting_router
from app.api.proxy import router as proxy_router
from app.api.ssl import router as ssl_router
from app.api.security import router as security_router
from app.api.ai_security import router as ai_security_router
from app.api.backups import router as backups_router
from app.api.updates import router as updates_router
from app.api.virtualization import router as virtualization_router
from app.api.audit import router as audit_router
from app.api.system import router as system_router
from app.api.auth import router as auth_router

__all__ = [
    "overview_router",
    "applications_router",
    "webhosting_router",
    "proxy_router",
    "ssl_router",
    "security_router",
    "ai_security_router",
    "backups_router",
    "updates_router",
    "virtualization_router",
    "audit_router",
    "system_router",
    "auth_router",
]
