from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token, user = auth_service.login(db, data)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=MeResponse)
def me(user=Depends(get_current_user)):
    return MeResponse(user=UserRead.model_validate(user))
