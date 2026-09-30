# System Overview

## End-to-end flow

```text
Hikvision Camera / NVR
        |
        v
Camera Provider Layer
        |
        v
Snapshot Engine
        |
        +----> Local Storage
        |
        +----> Database Record
        |
        +----> Cloud Sync
        |
        v
Snapshot Archive
        |
        v
FFmpeg Time-Lapse Generator
        |
        +----> MP4 Storage
        |
        +----> Cloud Sync
        |
        v
Time-Lapse Library
        |
        v
React Dashboard
```

## Technology stack

Backend:

- Python
- FastAPI
- SQLAlchemy
- Alembic
- SQLite
- FFmpeg

Frontend:

- React
- Vite
- Axios
- React Router

Infrastructure:

- Docker
- Docker Compose
- Nginx

Camera integration:

- Hikvision ISAPI
- HTTP Digest Authentication

## Roles

- Admin
- Operator
- Viewer

## Main operational modules

- Authentication
- Cameras
- Snapshot Policies
- Scheduler
- Snapshot Archive
- Time-Lapse Generator
- Time-Lapse Library
- Storage
- Cloud
- Monitoring
- Logs
