"""Pydantic schemas for authentication requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Password minimum 8 characters")
    full_name: str = Field(min_length=2, max_length=255, description="Full display name")
    preferred_language: str = Field(default="pt", max_length=10)


class UserLoginRequest(BaseModel):
    """Payload for credentials login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Payload for token refresh."""

    refresh_token: str


class TokenResponse(BaseModel):
    """JWT tokens returned upon successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Public user information response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    preferred_language: str
    selected_region_id: uuid.UUID | None
    created_at: datetime


class AuthResponse(BaseModel):
    """Complete response returned on login."""

    user: UserResponse
    tokens: TokenResponse
