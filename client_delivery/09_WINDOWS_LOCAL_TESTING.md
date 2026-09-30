# Windows Local Testing Guide

## Why this patch exists

Windows keeps SQLite files locked while a SQLAlchemy engine still has an open pooled connection. Older tests removed their temporary database directory immediately after the test body, which could cause:

```text
PermissionError: [WinError 32]
The process cannot access the file because it is being used by another process
```

Version 1.0.1 explicitly calls `engine.dispose()` in every temporary SQLite test before cleanup.

## Recommended test command

From PowerShell:

```powershell
cd C:\Users\Assem\Desktop\timelapse-system\backend
.\.venv\Scripts\python.exe -m pytest -q
```

Expected result:

```text
47 passed
```

## Integration / E2E regression

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m "integration or e2e" tests\test_phase17_integration_e2e.py
```

Expected result:

```text
7 passed
```

## If PowerShell blocks activation

You do not need to activate the virtual environment. Use the `.venv\Scripts\python.exe` commands directly.
