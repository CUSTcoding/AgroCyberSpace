"""User profile domain business service."""

from __future__ import annotations

from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserUpdateRequest


class UserService:
    """Handles business rules for user management and profile updates."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def update_profile(self, user: User, payload: UserUpdateRequest) -> User:
        """Apply non-null updates to an existing user profile."""
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()

        if payload.preferred_language is not None:
            user.preferred_language = payload.preferred_language.strip()

        if payload.selected_region_id is not None:
            user.selected_region_id = payload.selected_region_id

        return self.user_repo.update(user)
