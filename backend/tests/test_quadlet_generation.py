import os
from pathlib import Path
from app.services.podman_service import podman_service

def test_quadlet_specification_generation():
    quadlet_file = podman_service.generate_quadlet(
        app_id="test-portal",
        name="Test Portal",
        image="registry.csir.res.in/apps/test-portal:1.0.0",
        port=8090,
        memory_mb=512,
        cpu_percent=40,
        env_vars={"APP_ENV": "production"},
        volumes=["/srv/app-data/test:/data:Z"],
        read_only_root=True
    )

    assert os.path.exists(quadlet_file)
    with open(quadlet_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Mandatory security controls checks
    assert "ReadOnly=true" in content
    assert "DropCapability=ALL" in content
    assert "NoNewPrivileges=true" in content
    assert "UserNS=auto" in content
    assert "Memory=512M" in content
    assert "CPUQuota=40%" in content
    assert "HealthCmd=" in content
    assert "PublishPort=127.0.0.1:8090:8090" in content

def test_provenance_verification():
    prov = podman_service.verify_image_provenance("registry.csir.res.in/apps/test:1.0.0")
    assert prov["signature_verified"] is True
    assert prov["gate_status"] == "APPROVED"
    assert prov["vulnerabilities"]["critical"] == 0
