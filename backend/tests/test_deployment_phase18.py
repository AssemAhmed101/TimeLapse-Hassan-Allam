from pathlib import Path

import yaml

from app.core.config import cors_origins, trusted_hosts


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_docker_compose_has_required_services():
    compose_path = PROJECT_ROOT / "docker-compose.yml"
    assert compose_path.exists()

    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    assert "backend" in data["services"]
    assert "dashboard" in data["services"]
    assert data["services"]["backend"]["restart"] == "unless-stopped"
    assert data["services"]["dashboard"]["restart"] == "unless-stopped"


def test_deployment_files_exist():
    required = [
        PROJECT_ROOT / "backend" / "Dockerfile",
        PROJECT_ROOT / "dashboard" / "Dockerfile",
        PROJECT_ROOT / "dashboard" / "nginx.conf",
        PROJECT_ROOT / ".env.production.example",
        PROJECT_ROOT / "deployment" / "DEPLOYMENT.md",
    ]

    for path in required:
        assert path.exists(), str(path)


def test_production_env_template_has_critical_settings():
    text = (PROJECT_ROOT / ".env.production.example").read_text(
        encoding="utf-8"
    )

    assert "JWT_SECRET_KEY=" in text
    assert "CORS_ORIGINS=" in text
    assert "TRUSTED_HOSTS=" in text
    assert "CLOUD_PROVIDER=" in text


def test_nginx_proxies_api_to_backend():
    text = (
        PROJECT_ROOT / "dashboard" / "nginx.conf"
    ).read_text(encoding="utf-8")

    assert "location /api/" in text
    assert "proxy_pass http://backend:8000/api/" in text
    assert "try_files $uri $uri/ /index.html;" in text


def test_cors_and_trusted_host_helpers(monkeypatch):
    from app.core import config as config_module

    monkeypatch.setattr(
        config_module.settings,
        "CORS_ORIGINS",
        "https://one.example, https://two.example",
    )
    monkeypatch.setattr(
        config_module.settings,
        "TRUSTED_HOSTS",
        "one.example,two.example",
    )

    assert cors_origins() == [
        "https://one.example",
        "https://two.example",
    ]
    assert trusted_hosts() == [
        "one.example",
        "two.example",
    ]
