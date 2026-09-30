from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserRead, normalize_email


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class MeResponse(BaseModel):
    user: UserRead
