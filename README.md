# Tower Time-Lapse System

## Current Status

- Phase 0 — Project Foundation ✅
- Phase 1 — Backend Foundation + Simulator ✅
- Phase 2 — Database Layer ✅
- Phase 3 — Camera Management ✅
- Phase 4 — Snapshot Engine ✅
- Phase 5 — Scheduler ✅
- Phase 6 — Time-Lapse Generator ✅
- Phase 7 — Hikvision Integration ✅
- Phase 8 — Storage System ✅
- Phase 9 — Cloud Storage ✅
- Phase 10 — Web Dashboard Foundation ✅
- Phase 11 — Camera Dashboard ✅
- Phase 12 — Snapshot Archive ✅
- Phase 13 — Time-Lapse Library ✅
- Phase 14 — Custom Time-Lapse Builder ✅
- Phase 15 — Authentication & Permissions ✅
- Phase 16 — Monitoring & Reliability ✅

## Phase 15 — Authentication & Permissions

Implemented:
- Login screen
- JWT HS256 access tokens
- PBKDF2-SHA256 password hashing
- Protected dashboard routes
- Users and roles: admin / operator / viewer
- Admin user management page
- Protected JSON APIs
- Media access using authenticated token query for image/video tags
- Role guards for important write operations

### First-time setup

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts\create_admin.py
```

Then start backend and dashboard and sign in at:

```text
http://127.0.0.1:5173/login
```

Production requirement: set a strong `JWT_SECRET_KEY` in `.env`.

## Next Phase

Phase 16 — Monitoring & Reliability


## Phase 16 — Monitoring & Reliability

The system now includes operational health monitoring.

### Backend

- Rotating application logs
- Detailed health endpoint
- Database connectivity status
- Scheduler running status
- Scheduler cycle/failure counters
- Last scheduler cycle result
- Storage free-space monitoring
- Cloud configuration status
- Camera enabled/disabled counts
- Latest snapshot timestamp
- System uptime

### Monitoring API

```text
GET /api/v1/monitoring/health
GET /api/v1/monitoring/logs
```

Recent logs require an Admin or Operator account.

### Dashboard

The Settings page is now the system monitoring dashboard with:

- Overall status: OK / DEGRADED / CRITICAL
- Database status
- Scheduler status
- Storage usage
- Cloud state
- Camera state
- System warnings
- Recent application logs

## Next Phase

Phase 17 — Testing


## Phase 17 — Testing

Phase 17 adds integration and end-to-end verification of the complete system.

### Automated coverage added

- Authentication login and `/auth/me`
- Invalid login rejection
- Viewer permission restrictions
- Operator camera creation
- Simulator snapshot capture
- Snapshot archive retrieval
- Protected snapshot image access
- Time-lapse preview using real snapshot records
- Full end-to-end workflow:
  - Create camera
  - Capture snapshots
  - Generate MP4 with FFmpeg
  - Confirm database record
  - Confirm Time-Lapse Library entry
  - Stream generated MP4
- Monitoring endpoint authentication

### Run all backend tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

### Run the dedicated Phase 17 runner

```powershell
.\.venv\Scripts\python.exe scripts\run_phase17_tests.py
```

The FFmpeg end-to-end test is skipped only when FFmpeg is not installed.

## Next Phase

Phase 18 — Deployment


## Phase 18 — Deployment

The project now includes a production-style Docker deployment.

### Included

- FastAPI Docker image with FFmpeg
- React/Vite multi-stage production image
- Nginx reverse proxy
- Docker Compose stack
- Health checks
- Restart policies
- Persistent Docker volumes
- Production environment template
- Dynamic CORS origins
- Trusted host middleware
- Deployment documentation
- Backup starter script

### Quick start

```bash
cp .env.production.example .env.production
docker compose build
docker compose up -d
```

Create the first admin:

```bash
docker compose exec backend python scripts/create_admin.py
```

Full instructions:

```text
deployment/DEPLOYMENT.md
```

## Next Phase

Phase 19 — Final Client Delivery


## Phase 19 — Final Client Delivery

Version 1.1.0 is the current test release.

### Client delivery package

```text
client_delivery/
├── 01_SETUP_GUIDE.md
├── 02_ADMIN_GUIDE.md
├── 03_OPERATOR_GUIDE.md
├── 04_HANDOVER_CHECKLIST.md
├── 05_RELEASE_NOTES.md
├── 06_TROUBLESHOOTING.md
├── 07_CLIENT_ACCEPTANCE_TEST.md
├── 08_SYSTEM_OVERVIEW.md
└── system_manifest.json
```

### Final acceptance check

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\final_acceptance_check.py
```

## Project Status

Phase 0 through Phase 19 completed.

Current software release:

```text
1.2.0
```

Before live site acceptance, complete the client-specific Hikvision/network/cloud configuration and run the Client Acceptance Test.


## Version 1.0.1 — Windows Test Compatibility

This patch fixes Windows SQLite test cleanup failures (`WinError 32`) by explicitly disposing SQLAlchemy engines before temporary database files are removed. Production runtime behavior is unchanged.

## Windows Test Compatibility

The test suite includes Windows-safe SQLite cleanup for temporary test databases.
Temporary SQLAlchemy engines use `NullPool` and are explicitly disposed before
the temporary directory is removed. This prevents Windows `WinError 32` file-lock
failures during `pytest`.

Run the final suite on Windows with:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

Expected result for this release:

```text
47 passed
```


## Version 1.1.0 — High-Speed Capture Test

A controlled short-duration capture mode is available from the Time-Lapse page.

- 1.0 second interval (recommended first test)
- 0.5 second interval (best-effort)
- 2.0 second interval
- 5 / 10 / 15 minute test durations
- Live captured / failed / remaining counters
- Automatic stop at the selected duration
- One-click reuse of the captured test range in the Time-Lapse Builder
- Sub-second-safe snapshot filenames

For the first real NVR test, use **1 second for 15 minutes**. This targets about 900 snapshots. At 25 FPS the resulting time-lapse is about 36 seconds long.

## Version 1.2.0 — PTZ Marketing Capture

- Two dedicated PTZ cameras, each returning to a fixed preset before capture.
- 15-second stabilization delay before every snapshot.
- One validated JPEG every 6 hours per camera, running across the full 24 hours.
- 8 images per day total and 2,920 images per year.
- 8 TB planning forecast with 70%, 85% and 95% usage alerts.
- Original snapshots are retained indefinitely by default; cleanup requires an explicit retention value.
- At the conservative planning size of 20 MB per JPEG, snapshots consume about 57.031 GB/year and 8 TB holds about 143.64 years of images (excluding other NVR recordings and reserved disk space).

Apply database changes before starting the release:

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```
