import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional
from jose import jwt
from app.config import settings

def hash_payload(data: Any) -> str:
    """Computes a deterministic SHA-256 hash of any JSON-serializable data structure."""
    serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
