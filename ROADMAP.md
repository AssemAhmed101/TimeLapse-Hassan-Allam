# Tower Time-Lapse System — Roadmap

This roadmap defines the planned development phases for the complete Time-Lapse camera system.

---

## Phase 0 — Project Foundation ✅

### Goal
Create a clean and scalable project structure.

### Completed
- Backend structure
- Dashboard structure
- Storage folders
- Docs folder
- Tests folder
- Environment configuration
- README
- Clean `main.py`
- Central API router

### Result
The project is ready for modular development without putting all logic inside `main.py`.

---

## Phase 1 — Backend Foundation + Camera Simulator ✅

### Goal
Run the FastAPI backend and simulate a camera before connecting a real Hikvision camera.

### Completed
- FastAPI application
- Central API router
- Project configuration
- Logging setup
- Camera provider abstraction
- Camera simulator
- Camera service
- Snapshot service
- Camera status endpoint
- Snapshot endpoint
- Local snapshot storage

### Main Endpoints
- `GET /api/v1/health/`
- `GET /api/v1/cameras/status`
- `POST /api/v1/snapshots/`

### Result
The backend can simulate a camera and save snapshots locally.

---

## Phase 2 — Database Layer ✅

### Goal
Store cameras, snapshots, settings, and time-lapse records in a database.

### Tasks
- Configure SQLAlchemy
- Configure Alembic migrations
- Create Camera model
- Create Snapshot model
- Create TimeLapse model
- Create Settings model
- Create database session
- Add repository layer
- Add CRUD operations
- Link snapshots to cameras

### Initial Database
Development:
- SQLite

Production:
- PostgreSQL

### Result
Every camera, snapshot, and generated video will have a proper database record.

---

## Phase 3 — Camera Management ✅

### Goal
Manage multiple cameras from the system.

### Tasks
- Add camera
- Edit camera
- Delete camera
- Enable / disable camera
- Camera health status
- Camera connection test
- Store camera metadata
- Support multiple camera providers

### Camera Providers
- Simulator
- Hikvision Camera
- Hikvision NVR

### Result
The system can manage multiple physical cameras from one backend.

---

## Phase 4 — Snapshot Engine ✅

### Goal
Automatically capture snapshots from cameras.

### Tasks
- Manual snapshot capture
- Automatic snapshot capture
- Snapshot interval settings
- Capture schedule
- Start time / end time
- Enable / disable capture
- Snapshot naming rules
- Camera-based folder structure
- Error retry mechanism

### Example
Camera 01:
- Start: 07:00
- End: 18:00
- Interval: 5 minutes

### Result
The system captures images automatically without user interaction.

---

## Phase 5 — Scheduler ✅

### Goal
Run recurring jobs automatically.

### Tasks
- Configure APScheduler
- Snapshot jobs
- Daily time-lapse jobs
- Weekly time-lapse jobs
- Job recovery after restart
- Failed job logging

### Result
The backend can work automatically 24/7.

---

## Phase 6 — Time-Lapse Generator ✅

### Goal
Convert stored snapshots into MP4 time-lapse videos.

### Technology
- FFmpeg

### Tasks
- Install / detect FFmpeg
- Sort snapshots by time
- Generate MP4
- Configure FPS
- Configure output resolution
- Daily time-lapse
- Custom date-range time-lapse
- Generation progress
- Error handling
- Video metadata

### Example Flow
Snapshots  
→ Sort  
→ FFmpeg  
→ MP4  
→ Save  
→ Database record

### Result
The system automatically generates playable time-lapse videos.

---

## Phase 7 — Hikvision Integration ✅

### Goal
Replace the simulator with real Hikvision cameras.

### Requirements From IT
- Camera / NVR model
- IP address
- Username
- Password
- Network access
- Required ports

### Tasks
- Test camera connectivity
- Test snapshot endpoint
- Implement Hikvision provider
- Implement authentication
- Support ISAPI
- NVR support if required
- Connection timeout handling
- Offline camera handling

### Result
Snapshots come from the real tower cameras.

---

## Phase 8 — Storage System ✅

### Goal
Create a reliable storage layer for snapshots and videos.

### Tasks
- Local storage abstraction
- Camera folder organization
- Date folder organization
- File retention rules
- Automatic cleanup
- Disk usage monitoring
- Storage error handling

### Suggested Structure

```text
storage/
├── snapshots/
│   └── camera_001/
│       └── 2026-09-15/
│
└── timelapses/
    └── camera_001/
        └── 2026-09-15.mp4
```

### Result
Files are organized and easy to archive or move to cloud storage.

---

## Phase 9 — Cloud Storage ✅

### Goal
Upload snapshots and videos to cloud storage.

### Possible Providers
- AWS S3
- Cloudflare R2
- Azure Blob Storage
- Google Cloud Storage

### Tasks
- Cloud provider abstraction
- Upload snapshots
- Upload videos
- Retry failed uploads
- Signed URLs
- File synchronization
- Cloud retention policy

### Result
The project is no longer dependent on one local computer.

---

## Phase 10 — Web Dashboard Foundation ✅

### Goal
Create the user interface for operating the system.

### Main Pages
- Dashboard
- Cameras
- Snapshots
- Time-Lapses
- Settings

### Dashboard Overview
- Number of cameras
- Online / offline cameras
- Latest snapshots
- Latest generated videos
- System status
- Storage status

### Result
The client can manage the system visually instead of using FastAPI `/docs`.

---

## Phase 11 — Camera Dashboard ✅

### Goal
Manage cameras through the dashboard.

### Features
- Camera cards
- Camera status
- Last snapshot
- Capture snapshot button
- Start / stop capture
- Edit camera settings
- Snapshot interval
- Camera schedule

### Result
Camera operation can be controlled from the browser.

---

## Phase 12 — Snapshot Archive ✅

### Goal
Browse historical images.

### Features
- Filter by camera
- Filter by date
- Calendar
- Snapshot gallery
- Full image preview
- Download image
- Pagination

### Result
The client can inspect construction progress at any point in time.

---

## Phase 13 — Time-Lapse Library ✅

### Goal
Display generated time-lapse videos.

### Features
- Video player
- Camera filter
- Date filter
- Daily videos
- Weekly videos
- Custom videos
- Download video
- Generation status

### Result
The client can watch all generated time-lapses directly from the dashboard.

---

## Phase 14 — Custom Time-Lapse Builder ✅

### Goal
Allow the client to generate a time-lapse for any period.

### Example
Select:
- Camera 01
- From: 01/09/2026
- To: 15/09/2026
- FPS: 25

Then:
`Generate Time-Lapse`

### Tasks
- Date range selection
- Snapshot validation
- Queue generation job
- Progress status
- Save generated video

### Result
The client can create project progress videos on demand.

---

## Phase 15 — Authentication & Permissions ✅

### Goal
Secure the system.

### Tasks
- Login
- JWT authentication
- Password hashing
- Users
- Roles
- Admin permissions
- Viewer permissions
- Protected APIs

### Roles
Admin:
- Manage cameras
- Change settings
- Generate videos
- Manage users

Viewer:
- View snapshots
- Watch time-lapses
- Download allowed files

### Result
Only authorized users can access the system.

---

## Phase 16 — Monitoring & Reliability ✅

### Goal
Make the system reliable for long-term use.

### Tasks
- Camera offline detection
- Failed snapshot alerts
- Failed upload alerts
- Logging
- Health checks
- Storage monitoring
- Scheduler monitoring
- Database backup
- Restart recovery

### Result
The system can run unattended for long periods.

---

## Phase 17 — Testing ✅

### Goal
Verify the complete system before delivery.

### Tests
- Backend unit tests
- API tests
- Database tests
- Camera simulator tests
- Hikvision tests
- Snapshot interval tests
- FFmpeg tests
- Cloud upload tests
- Dashboard tests
- Failure recovery tests

### Real Camera Test
Run a real tower camera for:
- Several hours
- One full working day
- Multiple days if possible

### Result
The complete workflow is verified before deployment.

---

## Phase 18 — Deployment ✅

### Goal
Run the production system 24/7.

### Components
- Backend
- Dashboard
- PostgreSQL
- FFmpeg
- Cloud storage
- Reverse proxy
- HTTPS
- Docker

### Tasks
- Dockerize backend
- Dockerize dashboard
- Configure production database
- Configure cloud
- Configure environment variables
- Configure HTTPS
- Configure backup
- Configure restart policy

### Result
The system runs continuously without depending on a developer laptop.

---

## Phase 19 — Final Client Delivery ✅

### Deliverables
- Working Hikvision integration
- Automatic snapshots
- Automatic time-lapse generation
- Cloud storage
- Web dashboard
- Camera management
- Snapshot archive
- Time-lapse archive
- User login
- Production deployment
- Documentation
- Backup instructions
- Admin credentials
- Source code

### Final Workflow

```text
Hikvision Camera / NVR
        ↓
Snapshot Capture
        ↓
Backend
        ↓
Database
        ↓
Local Storage
        ↓
Cloud Storage
        ↓
FFmpeg Time-Lapse Generator
        ↓
Web Dashboard
        ↓
Client
```

---

# Current Status

✅ Phase 0 — Project Foundation  
✅ Phase 1 — Backend Foundation + Simulator  
✅ Phase 2 — Database Layer  
✅ Phase 3 — Camera Management  
✅ Phase 4 — Snapshot Engine  
✅ Phase 5 — Scheduler  
✅ Phase 6 — Time-Lapse Generator  
✅ Phase 7 — Hikvision Integration  
✅ Phase 8 — Storage System  
✅ Phase 9 — Cloud Storage  
✅ Phase 10 — Web Dashboard Foundation  
✅ Phase 11 — Camera Dashboard  
✅ Phase 12 — Snapshot Archive  
✅ Phase 13 — Time-Lapse Library  
✅ Phase 14 — Custom Time-Lapse Builder  
✅ Phase 15 — Authentication & Permissions  
✅ Phase 16 — Monitoring & Reliability  
✅ Phase 17 — Testing  
✅ Phase 18 — Deployment  
✅ Phase 19 — Final Client Delivery


## Release Status

**Version 1.1.0 — High-Speed Capture Test Ready ✅**
