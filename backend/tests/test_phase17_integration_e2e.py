from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import uuid

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.camera.simulator import SimulatorCamera
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User
from app.services.cloud_service import cloud_service
from app.services.storage_service import storage_service


@pytest.fixture()
def integration_env(tmp_path, monkeypatch):
    db_path = tmp_path / "phase17.db"
    engine = create_engine(
        f"sqlite:///{db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    storage_root = tmp_path / "storage"
    storage_service.root_path = storage_root
    storage_service.snapshots_path = storage_root / "snapshots"
    storage_service.timelapses_path = storage_root / "timelapses"
    storage_service.ensure_structure()

    monkeypatch.setattr(
        cloud_service,
        "upload_file",
        lambda path: {
            "success": True,
            "local_path": str(path),
            "cloud_url": "mock://phase17",
        },
    )

    def unique_snapshot(self):
        target = self.output_dir / datetime.now().strftime("%Y-%m-%d")
        target.mkdir(parents=True, exist_ok=True)
        path = target / f"{uuid.uuid4().hex}.jpg"
        Image.new("RGB", (640, 360), "white").save(path)
        return path

    monkeypatch.setattr(
        SimulatorCamera,
        "capture_snapshot",
        unique_snapshot,
    )

    yield {
        "Session": TestingSession,
        "client": TestClient(app),
        "storage_root": storage_root,
    }

    app.dependency_overrides.clear()
    engine.dispose()


def create_user(env, *, email, password, role):
    with env["Session"]() as db:
        user = User(
            email=email,
            full_name=role.title(),
            hashed_password=hash_password(password),
            role=role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id


def login(client, email, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_auth_login_and_me(integration_env):
    client = integration_env["client"]
    create_user(
        integration_env,
        email="admin@example.com",
        password="AdminPass123!",
        role="admin",
    )

    token = login(client, "admin@example.com", "AdminPass123!")
    response = client.get("/api/v1/auth/me", headers=auth(token))

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "admin@example.com"
    assert response.json()["user"]["role"] == "admin"


@pytest.mark.integration
def test_invalid_login_is_rejected(integration_env):
    client = integration_env["client"]
    create_user(
        integration_env,
        email="admin@example.com",
        password="AdminPass123!",
        role="admin",
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "wrong-password",
        },
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_viewer_cannot_create_camera(integration_env):
    client = integration_env["client"]
    create_user(
        integration_env,
        email="viewer@example.com",
        password="ViewerPass123!",
        role="viewer",
    )
    token = login(client, "viewer@example.com", "ViewerPass123!")

    response = client.post(
        "/api/v1/cameras/",
        headers=auth(token),
        json={
            "name": "Blocked Camera",
            "provider": "simulator",
            "is_enabled": True,
        },
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_operator_camera_snapshot_archive_and_media_auth(integration_env):
    client = integration_env["client"]
    create_user(
        integration_env,
        email="operator@example.com",
        password="OperatorPass123!",
        role="operator",
    )
    token = login(client, "operator@example.com", "OperatorPass123!")

    camera = client.post(
        "/api/v1/cameras/",
        headers=auth(token),
        json={
            "name": "Tower Simulator",
            "provider": "simulator",
            "is_enabled": True,
        },
    )
    assert camera.status_code == 201
    camera_id = camera.json()["id"]

    capture = client.post(
        f"/api/v1/snapshots/{camera_id}",
        headers=auth(token),
    )
    assert capture.status_code == 201
    snapshot = capture.json()["snapshot"]
    assert Path(snapshot["file_path"]).exists()

    archive = client.get(
        "/api/v1/snapshots/archive",
        headers=auth(token),
        params={"camera_id": camera_id},
    )
    assert archive.status_code == 200
    assert archive.json()["total"] == 1

    unauthenticated = client.get(
        f"/api/v1/snapshots/{snapshot['id']}/image"
    )
    assert unauthenticated.status_code == 401

    authenticated = client.get(
        f"/api/v1/snapshots/{snapshot['id']}/image",
        params={"token": token},
    )
    assert authenticated.status_code == 200
    assert authenticated.headers["content-type"].startswith("image/jpeg")


@pytest.mark.integration
def test_timelapse_preview_uses_real_snapshot_records(integration_env):
    client = integration_env["client"]
    create_user(
        integration_env,
        email="operator@example.com",
        password="OperatorPass123!",
        role="operator",
    )
    token = login(client, "operator@example.com", "OperatorPass123!")

    camera = client.post(
        "/api/v1/cameras/",
        headers=auth(token),
        json={
            "name": "Preview Camera",
            "provider": "simulator",
            "is_enabled": True,
        },
    )
    assert camera.status_code == 201
    camera_id = camera.json()["id"]

    for _ in range(4):
        response = client.post(
            f"/api/v1/snapshots/{camera_id}",
            headers=auth(token),
        )
        assert response.status_code == 201

    now = datetime.now(timezone.utc)
    preview = client.post(
        "/api/v1/timelapses/preview",
        headers=auth(token),
        json={
            "camera_id": camera_id,
            "start_at": (now - timedelta(minutes=5)).isoformat(),
            "end_at": (now + timedelta(minutes=5)).isoformat(),
            "fps": 2,
        },
    )

    assert preview.status_code == 200, preview.text
    body = preview.json()
    assert body["snapshot_count"] == 4
    assert body["can_generate"] is True
    assert body["estimated_duration_seconds"] == 2.0


@pytest.mark.e2e
@pytest.mark.skipif(
    shutil.which("ffmpeg") is None,
    reason="FFmpeg is required for the end-to-end generation test",
)
def test_camera_to_snapshot_to_mp4_to_library_flow(integration_env):
    client = integration_env["client"]
    create_user(
        integration_env,
        email="admin@example.com",
        password="AdminPass123!",
        role="admin",
    )
    token = login(client, "admin@example.com", "AdminPass123!")

    camera_response = client.post(
        "/api/v1/cameras/",
        headers=auth(token),
        json={
            "name": "E2E Tower Camera",
            "provider": "simulator",
            "is_enabled": True,
        },
    )
    assert camera_response.status_code == 201
    camera_id = camera_response.json()["id"]

    for _ in range(4):
        capture = client.post(
            f"/api/v1/snapshots/{camera_id}",
            headers=auth(token),
        )
        assert capture.status_code == 201

    now = datetime.now(timezone.utc)
    generate = client.post(
        "/api/v1/timelapses/generate",
        headers=auth(token),
        json={
            "camera_id": camera_id,
            "start_at": (now - timedelta(minutes=5)).isoformat(),
            "end_at": (now + timedelta(minutes=5)).isoformat(),
            "fps": 2,
            "output_width": 640,
            "output_height": 360,
        },
    )

    assert generate.status_code == 201, generate.text
    generated = generate.json()
    assert generated["snapshot_count"] == 4
    assert generated["timelapse"]["status"] == "completed"

    video_path = Path(generated["timelapse"]["file_path"])
    assert video_path.exists()
    assert video_path.stat().st_size > 0

    library = client.get(
        "/api/v1/timelapses/library",
        headers=auth(token),
        params={"camera_id": camera_id},
    )
    assert library.status_code == 200
    assert library.json()["total"] == 1
    item = library.json()["items"][0]
    assert item["status"] == "completed"

    video = client.get(
        f"/api/v1/timelapses/{item['id']}/video",
        params={"token": token},
    )
    assert video.status_code == 200
    assert video.headers["content-type"].startswith("video/mp4")
    assert len(video.content) > 0


@pytest.mark.integration
def test_protected_monitoring_requires_authentication(integration_env):
    client = integration_env["client"]
    response = client.get("/api/v1/monitoring/health")
    assert response.status_code == 401
