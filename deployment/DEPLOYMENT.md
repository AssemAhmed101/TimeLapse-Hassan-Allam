# Production Deployment Guide

## Recommended architecture

```text
Browser
  |
  v
Nginx Dashboard Container :80/:443
  |              |
  | React SPA    +---- /api/* ----> FastAPI Container :8000
  |
Docker named volumes
  |- SQLite database
  |- Snapshots / MP4 files
  |- Application logs
```

## Server requirements

Recommended minimum for a small installation:

- Ubuntu 24.04 LTS or similar Linux server
- 4 CPU cores
- 8 GB RAM
- SSD storage sized for the expected snapshot retention period
- Docker Engine
- Docker Compose v2
- Stable network path to the Hikvision camera/NVR

More cameras, 4K image processing, or heavy concurrent time-lapse generation
may require more CPU, RAM, and storage.

## 1. Prepare configuration

From the project root:

```bash
cp .env.production.example .env.production
```

Edit `.env.production`.

You must change at least:

```text
JWT_SECRET_KEY
CORS_ORIGINS
TRUSTED_HOSTS
```

Do not commit `.env.production`.

## 2. Start the system

```bash
docker compose build
docker compose up -d
```

Check:

```bash
docker compose ps
docker compose logs -f
```

Open the server IP or domain in the browser.

## 3. Create the first admin

```bash
docker compose exec backend python scripts/create_admin.py
```

## 4. Health checks

Backend container health:

```text
/api/v1/health/
```

Authenticated detailed monitoring:

```text
/api/v1/monitoring/health
```

Dashboard container:

```text
/healthz
```

## 5. Persistent data

Docker volumes store:

- SQLite database
- Snapshots
- Generated MP4 videos
- Backend logs

Container recreation does not delete these volumes unless they are explicitly removed.

Never run:

```bash
docker compose down -v
```

on a production system unless you intentionally want to delete the named volumes.

## 6. Updating the application

```bash
git pull
docker compose build
docker compose up -d
docker compose ps
```

The backend runs Alembic migrations automatically during container startup.

## 7. HTTPS

For public/remote access, place a TLS-capable reverse proxy or load balancer
in front of the dashboard container, such as:

- Nginx
- Caddy
- Traefik
- Cloudflare Tunnel / reverse proxy where appropriate

Use HTTPS for all production remote access.

## 8. Camera network access

The backend server must be able to reach the Hikvision camera/NVR IP and port.
For an on-site camera network, the preferred deployment is usually:

- server on the same LAN/VLAN, or
- a secure site-to-site VPN

Avoid exposing camera management ports directly to the public internet.

## 9. Backups

Back up at minimum:

- database volume
- storage volume
- `.env.production` in a secure secret store

A starter script is included at:

```text
deployment/backup.sh
```

Test restoration before relying on backups operationally.

## 10. Production checklist

- Strong JWT secret configured
- Admin account created
- Correct domain / trusted hosts configured
- HTTPS enabled for remote use
- Hikvision connectivity verified
- Cloud credentials configured if using real cloud storage
- Storage retention reviewed
- Backup and restore tested
- Monitoring checked
- Docker restart policy verified
