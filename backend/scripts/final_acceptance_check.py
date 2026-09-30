from pathlib import Path
import json
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def require(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")


def main():
    required = [
        PROJECT_ROOT / "docker-compose.yml",
        PROJECT_ROOT / ".env.production.example",
        PROJECT_ROOT / "deployment" / "DEPLOYMENT.md",
        PROJECT_ROOT / "client_delivery" / "01_SETUP_GUIDE.md",
        PROJECT_ROOT / "client_delivery" / "02_ADMIN_GUIDE.md",
        PROJECT_ROOT / "client_delivery" / "03_OPERATOR_GUIDE.md",
        PROJECT_ROOT / "client_delivery" / "04_HANDOVER_CHECKLIST.md",
        PROJECT_ROOT / "client_delivery" / "05_RELEASE_NOTES.md",
        PROJECT_ROOT / "client_delivery" / "07_CLIENT_ACCEPTANCE_TEST.md",
        PROJECT_ROOT / "client_delivery" / "system_manifest.json",
    ]

    for item in required:
        require(item)

    manifest = json.loads(
        (PROJECT_ROOT / "client_delivery" / "system_manifest.json").read_text(
            encoding="utf-8"
        )
    )

    if manifest["version"] != "1.0.1":
        raise SystemExit("Manifest version mismatch")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=PROJECT_ROOT / "backend",
    )

    if result.returncode != 0:
        raise SystemExit(result.returncode)

    print("Final acceptance check passed.")


if __name__ == "__main__":
    main()
