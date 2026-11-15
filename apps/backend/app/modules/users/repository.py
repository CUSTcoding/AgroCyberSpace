"""Repository layer for User database operations."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.models import User


class UserRepository:
    """Encapsulates database access for the User entity."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Find a user by unique UUID."""
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> User | None:
        """Find a user by email address (case-insensitive search)."""
        stmt = select(User).where(func.lower(User.email) == func.lower(email.strip()))
        return self.db.scalars(stmt).first()

    def create(self, user: User) -> User:
        """Persist a new user entity to the database."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Commit updates to an existing user."""
        self.db.commit()
        self.db.refresh(user)
        return user

    def list(self, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        """Return a paginated list of users along with total count."""
        count_stmt = select(func.count(User.id))
        total = self.db.scalar(count_stmt) or 0

        stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total
