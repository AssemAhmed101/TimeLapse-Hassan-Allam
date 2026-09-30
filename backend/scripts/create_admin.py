from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from getpass import getpass

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.repositories.user_repository import user_repository
from app.schemas.user import normalize_email


def main():
    email = normalize_email(input("Admin email: ").strip())
    full_name = input("Full name: ").strip() or "Administrator"
    password = getpass("Password (minimum 8 characters): ")
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters")

    db = SessionLocal()
    try:
        if user_repository.get_by_email(db, email):
            raise SystemExit("A user with this email already exists")
        user = user_repository.create(
            db, email=email, full_name=full_name,
            hashed_password=hash_password(password),
            role="admin", is_active=True,
        )
        print(f"Admin created: #{user.id} {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
