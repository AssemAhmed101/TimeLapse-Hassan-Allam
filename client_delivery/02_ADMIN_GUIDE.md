# Tower Time-Lapse System — Admin Guide

## Admin responsibilities

Administrators can manage:

- Users
- Cameras
- Snapshot policies
- Time-lapse generation
- Storage
- Cloud
- Monitoring
- Logs

## User roles

### Admin

Full administrative access.

### Operator

Operational control such as:

- Camera management
- Snapshot capture
- Time-lapse generation
- Monitoring logs

### Viewer

Read-only style access to authorized dashboard content.

## First admin

Create the first admin from the server:

```bash
docker compose exec backend python scripts/create_admin.py
```

## User management

Admins can:

- Create users
- Change roles
- Enable/disable users
- Update passwords
- Delete users

## Camera management

For each Hikvision camera/NVR verify:

- Provider type
- Host/IP
- Username
- Password
- Scheme
- Port
- Channel
- Enabled state

## Snapshot policy

Recommended initial settings should be confirmed with the client based on:

- site working hours
- required final time-lapse duration
- storage capacity
- project duration

## Storage management

Monitor:

- free disk space
- snapshot count
- video count
- retention period

Use cleanup in dry-run mode before deleting production files.

## Cloud

Current architecture supports:

- local mock storage
- AWS S3
- Cloudflare R2
- generic S3-compatible storage

Test uploads before relying on cloud backup.

## Logs

Monitoring logs are available to Admin and Operator roles.

Backend logs are persisted in the Docker log volume.

## Backup

Back up:

- SQLite database volume
- snapshot/video storage volume
- production environment secrets

A starter backup script is included:

```text
deployment/backup.sh
```

## Updating

Typical update flow:

```bash
git pull
docker compose build
docker compose up -d
docker compose ps
```

Database migrations run automatically when the backend starts.
