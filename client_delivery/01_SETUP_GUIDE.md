# Tower Time-Lapse System — Setup Guide

Version: 1.1.0

## Purpose

This guide explains how to install and start the production system on the client server.

## Recommended server

Minimum recommended starting point for a small installation:

- Ubuntu 24.04 LTS or similar Linux server
- 4 CPU cores
- 8 GB RAM
- SSD storage
- Stable LAN/VLAN access to Hikvision camera/NVR
- Docker Engine
- Docker Compose v2

## 1. Copy project to server

Place the complete project on the server.

## 2. Create production environment file

From the project root:

```bash
cp .env.production.example .env.production
```

Edit `.env.production`.

Change at minimum:

```text
JWT_SECRET_KEY
CORS_ORIGINS
TRUSTED_HOSTS
```

If using AWS S3 / Cloudflare R2 / S3-compatible storage, also configure the cloud credentials.

## 3. Start containers

```bash
docker compose build
docker compose up -d
```

## 4. Confirm status

```bash
docker compose ps
```

Both `timelapse-backend` and `timelapse-dashboard` should be healthy/running.

## 5. Create first admin account

```bash
docker compose exec backend python scripts/create_admin.py
```

Enter:

- Admin email
- Full name
- Strong password

## 6. Open the dashboard

Open the server IP or configured domain in a browser.

Example:

```text
http://SERVER-IP
```

or, when HTTPS is configured:

```text
https://timelapse.example.com
```

## 7. Add the first camera

From the Cameras page:

1. Choose Hikvision Camera or Hikvision NVR.
2. Enter the camera/NVR IP address.
3. Enter username and password.
4. Set port and channel.
5. Save.
6. Use Test Connection.

## 8. Configure snapshot policy

For each camera configure:

- Capture interval
- Start time
- End time
- Retry count
- Retry delay
- Enabled/disabled state

## 9. Verify storage and monitoring

Open Monitoring & Reliability and confirm:

- Database: Online
- Scheduler: Running
- Storage: Healthy
- Camera: Enabled
- Cloud: Configured when applicable

## 10. Verify first snapshot

Use Capture Snapshot and confirm the image appears in Snapshot Archive.

## 11. Generate a test time-lapse

Open Time-Lapses:

1. Choose the camera.
2. Choose date/time range.
3. Select FPS.
4. Select output resolution.
5. Preview.
6. Generate.

The MP4 should appear in the Time-Lapse Library.

## 12. Production safety

Do not expose Hikvision camera management ports directly to the public internet.

Use:

- LAN/VLAN access
- site-to-site VPN
- secure reverse proxy for the web application
- HTTPS for remote access
