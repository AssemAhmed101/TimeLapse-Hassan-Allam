from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import user_repository

bearer = HTTPBearer(auto_error=False)


def _resolve_user(token: str, db: Session) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = user_repository.get(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User account unavailable")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return _resolve_user(credentials.credentials, db)


def get_current_media_user(
    token: str | None = Query(default=None),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    raw = credentials.credentials if credentials is not None else token
    if not raw:
        raise HTTPException(status_code=401, detail="Authentication required")
    return _resolve_user(raw, db)


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency
