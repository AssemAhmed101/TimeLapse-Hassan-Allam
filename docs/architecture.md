# Architecture

Camera / NVR
    |
    v
Camera Provider Layer
    |
    v
FastAPI Backend
    |---- Snapshot Service
    |---- Scheduler
    |---- Time-Lapse Generator (FFmpeg)
    |---- Storage / Cloud
    |---- Database
    |
    v
REST API
    |
    v
Web Dashboard

The project keeps API routes, business logic, camera integrations, persistence,
scheduled jobs, and frontend concerns separated.
