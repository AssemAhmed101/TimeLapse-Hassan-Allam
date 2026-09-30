# Tested Delivery Report

Project: Tower Time-Lapse System v1.2.0  
Test date: 2026-09-24  
Delivery status: PASSED

## Verification Results

- ZIP integrity: passed; all 232 original archive entries extracted without errors.
- Backend automated tests: 59 passed.
- Database migration: upgraded successfully from a new SQLite database to Alembic revision `0005 (head)`.
- Dashboard dependency installation: completed successfully from `package-lock.json`.
- Dashboard production build: completed successfully with Vite 6.4.3.

## Project-Specific Checks

- Capture interval: exactly 21,600 seconds (6 hours).
- Capture window: full 24 hours, including day and night.
- Camera count: 2 PTZ cameras.
- Expected daily output: 4 images per camera; 8 images total per day.
- Storage retention: open-ended when retention values are set to zero.
- Storage forecast: 2,920 images/year, approximately 57.031 GB/year at the configured estimate.
- 8 TB estimated capacity: approximately 143.64 years at that estimate.
- Storage alerts: warning at 70%, high at 85%, and critical at 95%.

## Note

The automated checks validate application logic, database migration, and dashboard compilation. Final on-site acceptance must also test the real PTZ camera credentials, preset position, NVR access, network connectivity, and an actual JPEG capture from each camera.
