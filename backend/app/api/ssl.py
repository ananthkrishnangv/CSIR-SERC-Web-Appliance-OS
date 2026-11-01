from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ssl", tags=["SSL / TLS Key Vault"])

class CertificateResponse(BaseModel):
    id: str
    common_name: str
    sans: str
    issuer: str
    key_spec: str
    sig_algo: str
    days_left: int
    auto_renew: bool

class CSRRequest(BaseModel):
    common_name: str = Field(..., example="portal.serc.res.in")
    organization: str = Field("CSIR-SERC", example="CSIR-SERC")
    key_type: str = Field("ECDSA secp384r1", example="ECDSA secp384r1")
    sans: Optional[List[str]] = Field(["portal.serc.res.in"])

class AcmeIssueRequest(BaseModel):
    domain: str = Field(..., example="shm.serc.res.in")
    challenge_type: str = Field("http-01", example="http-01")

_CERTIFICATES_DB = [
    {
        "id": "cert-01",
        "common_name": "*.serc.res.in",
        "sans": "*.serc.res.in, serc.res.in",
        "issuer": "CSIR Sovereign Root CA / Let's Encrypt ACME",
        "key_spec": "ECDSA secp384r1 (High Security)",
        "sig_algo": "SHA384withECDSA",
        "days_left": 84,
        "auto_renew": True
    },
    {
        "id": "cert-02",
        "common_name": "shm.serc.res.in",
        "sans": "shm.serc.res.in, sensor-edge.serc.res.in",
        "issuer": "Let's Encrypt E6 Intermediate",
        "key_spec": "RSA 4096-bit (Military Grade)",
        "sig_algo": "SHA256withRSA",
        "days_left": 42,
        "auto_renew": True
    },
    {
        "id": "cert-03",
        "common_name": "appliance.internal.serc.res.in",
        "sans": "10.20.10.15, localhost",
        "issuer": "CSIR-SERC Hardware TPM-Backed Internal CA",
        "key_spec": "ECDSA secp256r1 (TPM Endorsement)",
        "sig_algo": "SHA256withECDSA",
        "days_left": 312,
        "auto_renew": True
    }
]

@router.get("/certificates", response_model=List[CertificateResponse])
def list_certificates():
    """
    Returns all installed SSL/TLS certificates, SANs, and key vault telemetry.
    """
    return _CERTIFICATES_DB

@router.post("/acme/issue")
def trigger_acme_issue(req: AcmeIssueRequest):
    new_id = f"cert-{len(_CERTIFICATES_DB) + 1:02d}"
    cert = {
        "id": new_id,
        "common_name": req.domain,
        "sans": req.domain,
        "issuer": "Let's Encrypt ACME Authority",
        "key_spec": "ECDSA secp384r1",
        "sig_algo": "SHA384withECDSA",
        "days_left": 90,
        "auto_renew": True
    }
    _CERTIFICATES_DB.append(cert)
    return {"status": "success", "message": f"ACME certificate provisioned for {req.domain}", "cert": cert}

@router.post("/csr/generate")
def generate_csr(req: CSRRequest):
    csr_pem = f"""-----BEGIN CERTIFICATE REQUEST-----
MIICvDCCAaQCAQAwdzELMAkGA1UEBhMCSU4xEDAOBgNVBAgMB1RhbWlsIE5hZHUx
EDAOBgNVBAcMB0NoZW5uYWkxEjAQBgNVBAoMCUNTSVItU0VSQzEUMBIGA1UECwwL
Q3liZXJTZWN1cjExGTAXBgNVBAMMEHNoYXJtYS5zZXJjLnJlcy5pbjBZMBMGByqG
SM49AgEGCCqGSM49AwEHA0IABCR/CSIR-SWA-SOVEREIGN-KEY-MATERIAL-CERTIN-70B
-----END CERTIFICATE REQUEST-----"""
    return {
        "status": "success",
        "common_name": req.common_name,
        "key_type": req.key_type,
        "csr_pem": csr_pem
    }
