# Update from 1.0.1 to 1.1.0

This update adds the High-Speed Capture Test without requiring a database migration.

## Preserve your current local data

Do not replace these runtime files with a clean copy:

- `backend/timelapse.db`
- `backend/.env`
- `storage/`
- `backend/.venv/`
- `dashboard/node_modules/`

The provided **high-speed-update** ZIP intentionally excludes the database, `.env`, storage files, virtual environment, and node_modules.

## Update steps on Windows

1. Stop the Backend and Dashboard terminals.
2. Make a backup copy of `backend/timelapse.db` and the `storage` folder.
3. Extract the update ZIP over `C:\Users\Assem\Desktop\timelapse-system` and allow Windows to replace code files.
4. Start both services with `windows-start-all.cmd`, or use the normal two terminal commands.
5. Open `http://localhost:5173`.
6. Go to **Time-Lapses** and use **High-Speed Capture Test**.

Recommended first test: **1 second / 15 minutes / 25 FPS / 720p**.
