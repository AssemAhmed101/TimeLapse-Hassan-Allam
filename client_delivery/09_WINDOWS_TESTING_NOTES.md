# Windows Testing Notes

The final test suite has been updated for Windows SQLite file-lock behavior.

## Why WinError 32 happened

SQLAlchemy connection pooling could keep a handle open to a temporary SQLite
database after a test finished. Windows does not allow `TemporaryDirectory` to
delete that database while the handle is still open.

## Fix applied

Database tests now:

- use SQLAlchemy `NullPool` for temporary SQLite engines
- call `engine.dispose()` before temporary directories are removed

## Final command

```powershell
cd C:\Users\Assem\Desktop\timelapse-system\backend
.\.venv\Scripts\python.exe -m pytest -q
```

Expected result:

```text
47 passed
```
