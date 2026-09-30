import os
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "CSIR Secure Web Appliance OS"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = Path(os.getenv("CSIR_DATA_DIR", str(Path(__file__).resolve().parent.parent / "data")))
    LOG_DIR: Path = Path(os.getenv("CSIR_LOG_DIR", str(Path(__file__).resolve().parent.parent / "data" / "logs")))
    AUDIT_LEDGER_PATH: Path = DATA_DIR / "csir_audit.ledger"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'csir_swa.db'}")
    
    # Security & Tokens
    SECRET_KEY: str = os.getenv("CSIR_SECRET_KEY", "csir-swa-strategic-secure-key-2026-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8
    
    # Node Agent Socket / RPC
    NODE_AGENT_SOCKET: str = os.getenv("NODE_AGENT_SOCKET", "/run/csir-swa/agent.sock")
    NODE_AGENT_MOCK: bool = os.getenv("NODE_AGENT_MOCK", "true").lower() in ("true", "1", "yes")

    # Appliance Channels
    CURRENT_CHANNEL: str = "Stable"
    SUPPORTED_CHANNELS: list[str] = ["LTS", "Stable", "Pilot", "Security", "Emergency", "Air-gap", "Development"]
    
    # CERT-In Compliance settings
    CERT_IN_REPORTING_HOURS: int = 6
    LOG_RETENTION_DAYS: int = 180
    NTP_SERVERS: list[str] = ["time.nplindia.org", "ntp.nic.in"]

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
