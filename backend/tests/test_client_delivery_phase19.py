from pathlib import Path
import json

from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_release_version_is_1_1_0():
    assert settings.VERSION == "1.2.0"


def test_client_delivery_package_exists():
    delivery = PROJECT_ROOT / "client_delivery"

    required = [
        "01_SETUP_GUIDE.md",
        "02_ADMIN_GUIDE.md",
        "03_OPERATOR_GUIDE.md",
        "04_HANDOVER_CHECKLIST.md",
        "05_RELEASE_NOTES.md",
        "06_TROUBLESHOOTING.md",
        "07_CLIENT_ACCEPTANCE_TEST.md",
        "08_SYSTEM_OVERVIEW.md",
        "system_manifest.json",
    ]

    for name in required:
        assert (delivery / name).exists(), name


def test_system_manifest():
    path = PROJECT_ROOT / "client_delivery" / "system_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))

    assert manifest["version"] == "1.2.0"
    assert manifest["delivery_phase"] == 19
    assert "hikvision" in manifest["camera_providers"]
    assert "admin" in manifest["roles"]
    assert manifest["phases_completed"] == list(range(0, 20))


def test_handover_checklist_has_critical_sections():
    text = (
        PROJECT_ROOT
        / "client_delivery"
        / "04_HANDOVER_CHECKLIST.md"
    ).read_text(encoding="utf-8")

    for section in [
        "Infrastructure",
        "Application",
        "Accounts",
        "Cameras",
        "Time-Lapse",
        "Storage & Cloud",
        "Monitoring",
        "Client acceptance",
    ]:
        assert section in text


def test_acceptance_document_has_signoff():
    text = (
        PROJECT_ROOT
        / "client_delivery"
        / "07_CLIENT_ACCEPTANCE_TEST.md"
    ).read_text(encoding="utf-8")

    assert "Client representative" in text
    assert "System provider representative" in text
    assert "Signature" in text
