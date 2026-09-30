# Troubleshooting Guide

## Dashboard shows Backend Offline

Check:

```bash
docker compose ps
docker compose logs backend
```

Confirm the backend health endpoint responds.

## Camera connection fails

Verify:

- IP address
- network route
- port
- protocol
- username
- password
- channel

From the server, confirm the camera/NVR is reachable on the expected network.

## No snapshots

Check:

- camera is enabled
- snapshot policy is enabled
- current time is inside the capture window
- scheduler is running
- storage has free space

## Time-lapse cannot be generated

Confirm:

- at least two snapshots exist
- the selected range includes images
- FFmpeg is installed in the backend container
- output storage is writable

## Low storage

Review retention settings.

Run cleanup as dry-run before deleting data.

## Login fails

Check:

- correct email
- correct password
- account is active

Admin can reset/update the account.

## Container restart loop

Check:

```bash
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 dashboard
```

## Database migration error

Check backend logs and confirm the database volume is writable.

Back up production data before manually changing migration state.
