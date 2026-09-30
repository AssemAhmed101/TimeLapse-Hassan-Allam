from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.auth_service import auth_service

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return auth_service.list_users(db)


@router.post("/", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return auth_service.create_user(db, data)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return auth_service.update_user(db, user_id, data)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    auth_service.delete_user(db, user_id, current_user_id=admin.id)
    return {"success": True, "deleted_user_id": user_id}
