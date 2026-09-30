# Tower Time-Lapse System — Operator Guide

## Daily use

### Dashboard

Use the Dashboard to review:

- backend status
- camera count
- snapshots
- time-lapses
- storage
- cloud state

### Cameras

Use Cameras to:

- check camera status
- test connection
- enable/disable a camera
- capture a manual snapshot

### Snapshots

Use Snapshot Archive to:

- browse captured images
- filter by camera
- filter by date
- preview images
- download images

### Time-Lapses

Use the Time-Lapse Library to:

- browse generated videos
- play MP4 videos
- filter results
- download videos

### Generate a custom time-lapse

1. Open Time-Lapses.
2. Select a camera.
3. Select start date/time.
4. Select end date/time.
5. Choose FPS.
6. Choose resolution.
7. Click Preview.
8. Confirm snapshots are available.
9. Click Generate Time-Lapse.

## Monitoring

Open Monitoring & Reliability.

Normal status:

```text
OK
```

Possible warning status:

```text
DEGRADED
```

Critical status:

```text
CRITICAL
```

If the system is degraded, check:

- database
- scheduler
- storage space
- cloud state
- cameras

## If a camera is offline

1. Check camera power.
2. Check network connection.
3. Confirm IP address.
4. Confirm port.
5. Confirm username/password.
6. Confirm channel.
7. Run Test Connection.
8. Contact IT/network support if the camera is unreachable from the server.

## If snapshots stop

Check:

- camera enabled state
- snapshot policy enabled
- working-hour window
- scheduler status
- camera network connection
- free disk space

## If a video fails

Check:

- at least two snapshots exist
- date range is correct
- FFmpeg is available
- storage has enough free space
- logs for error details
