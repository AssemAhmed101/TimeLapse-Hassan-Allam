from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate, UserUpdate


class AuthService:
    def login(self, db: Session, data: LoginRequest):
        user = user_repository.get_by_email(db, data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is disabled")
        return create_access_token(str(user.id), user.role), user

    def list_users(self, db: Session):
        return user_repository.list(db)

    def create_user(self, db: Session, data: UserCreate):
        if user_repository.get_by_email(db, data.email):
            raise HTTPException(status_code=409, detail="Email already exists")
        return user_repository.create(
            db, email=data.email, full_name=data.full_name,
            hashed_password=hash_password(data.password), role=data.role,
            is_active=data.is_active,
        )

    def update_user(self, db: Session, user_id: int, data: UserUpdate):
        user = user_repository.get(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        updates = data.model_dump(exclude_unset=True)
        if "password" in updates:
            user.hashed_password = hash_password(updates.pop("password"))
        for field, value in updates.items():
            setattr(user, field, value)
        return user_repository.save(db, user)

    def delete_user(self, db: Session, user_id: int, current_user_id: int | None = None):
        user = user_repository.get(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user_id is not None and user.id == current_user_id:
            raise HTTPException(status_code=409, detail="You cannot delete your own account")
        user_repository.delete(db, user)


auth_service = AuthService()
