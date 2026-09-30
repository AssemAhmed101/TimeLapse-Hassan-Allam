# Release Notes — Version 1.1.0

## Product

Tower Time-Lapse System

## Release

Production Release Candidate / Client Delivery

## Main capabilities

- Hikvision Camera integration
- Hikvision NVR integration
- Camera simulator
- Automated snapshot capture
- Per-camera snapshot policy
- Background scheduler
- Snapshot archive
- FFmpeg MP4 generation
- Time-Lapse Library
- Custom Time-Lapse Builder
- Local storage management
- Storage retention cleanup
- S3-compatible cloud abstraction
- User authentication
- JWT authorization
- Admin / Operator / Viewer roles
- Monitoring & reliability dashboard
- Logs
- Docker deployment
- Nginx reverse proxy
- Persistent data volumes
- Production configuration templates

## Testing status

The automated suite includes:

- unit tests
- repository/service tests
- authentication tests
- role/permission tests
- integration tests
- end-to-end workflow tests
- FFmpeg MP4 generation test
- deployment configuration tests

## Known production dependencies

Real deployment still requires client-specific values:

- Hikvision IP/credentials
- correct NVR/camera channels
- server network access
- production hostname/domain
- HTTPS configuration when remote access is required
- real cloud credentials when using S3/R2
- client-approved retention settings

## Security notes

Before production:

- replace the default JWT secret
- protect `.env.production`
- use HTTPS for remote access
- do not expose Hikvision camera ports directly to the internet
- use strong camera and application passwords
- restrict server access


## Version 1.0.1 Fixes

- Fixed Windows `WinError 32` failures in the automated SQLite test suite.
- SQLAlchemy test engines are now explicitly disposed before temporary database directories are removed.
- This change targets Windows file-locking behavior and does not change production database logic.
- Full backend regression suite remains green after the compatibility fix.

## Version 1.1.0 — High-Speed Capture Test

- Added short-duration high-speed capture mode for NVR/camera testing.
- 1.0s, 0.5s best-effort, and 2.0s capture intervals.
- 5, 10, and 15 minute controlled test sessions.
- Live capture progress, success/failure counters, and automatic stop.
- Sub-second-safe snapshot filenames.
- One-click reuse of the test time range in the Time-Lapse Builder.
- Increased Time-Lapse generation request timeout for large snapshot sets.
- Fixed direct Windows execution of `scripts/create_admin.py`.
