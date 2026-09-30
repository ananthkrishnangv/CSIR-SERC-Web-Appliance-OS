from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])

class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: str = "123456"

@router.post("/login")
def login_for_access_token(req: LoginRequest):
    # In production: validates against local shadow, LDAP or Keycloak/OIDC
    if req.username in ["admin", "admin@csir.res.in", "sec-officer"]:
        token = create_access_token({
            "sub": req.username,
            "role": "admin",
            "mfa_verified": True
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": req.username,
                "role": "Administrator",
                "email": f"{req.username}@csir.res.in" if "@" not in req.username else req.username
            }
        }
    raise HTTPException(status_code=401, detail="Invalid appliance credentials or MFA token.")

@router.get("/me")
def get_current_user():
    return {
        "username": "admin@csir.res.in",
        "name": "System Administrator",
        "role": "Security Administrator",
        "permissions": ["all"],
        "mfa_enabled": True
    }
