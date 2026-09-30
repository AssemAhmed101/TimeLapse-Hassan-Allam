from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.database.base import Base
from app.repositories.user_repository import UserRepository


def test_password_hash_and_verify():
    value = hash_password("Password123!")
    assert value != "Password123!"
    assert verify_password("Password123!", value) is True
    assert verify_password("wrong-password", value) is False


def test_jwt_roundtrip():
    token = create_access_token("42", "admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_user_repository_create_and_lookup():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "auth.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        repo = UserRepository()
        with Session() as db:
            created = repo.create(
                db, email="admin@example.com", full_name="Admin",
                hashed_password=hash_password("Password123!"),
                role="admin", is_active=True,
            )
            found = repo.get_by_email(db, "ADMIN@example.com")
            assert found is not None
            assert found.id == created.id
            assert found.role == "admin"
        engine.dispose()
