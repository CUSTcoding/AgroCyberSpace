"""Pydantic schemas for User profile management."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from app.modules.auth.schemas import UserResponse


class UserUpdateRequest(BaseModel):
    """Payload for updating user profile information."""

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    preferred_language: str | None = Field(default=None, max_length=10)
    selected_region_id: uuid.UUID | None = Field(default=None)


__all__ = ["UserResponse", "UserUpdateRequest"]
