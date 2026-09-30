from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def list(self, db: Session) -> list[User]:
        return list(db.scalars(select(User).order_by(User.id)).all())

    def get(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def get_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email.strip().lower())
        return db.scalar(stmt)

    def create(self, db: Session, *, email: str, full_name: str, hashed_password: str, role: str, is_active: bool) -> User:
        user = User(
            email=email.strip().lower(), full_name=full_name.strip(),
            hashed_password=hashed_password, role=role, is_active=is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def save(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User) -> None:
        db.delete(user)
        db.commit()


user_repository = UserRepository()
