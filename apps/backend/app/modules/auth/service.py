"""Authentication domain business logic service."""

from __future__ import annotations

import uuid

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.shared.exceptions import ConflictException, UnauthorizedException


class AuthService:
    """Handles business rules for user registration, authentication and JWT tokens."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register(self, payload: UserRegisterRequest) -> User:
        """Register a new player account."""
        existing_user = self.user_repo.get_by_email(payload.email)
        if existing_user is not None:
            raise ConflictException(f"Email '{payload.email}' is already registered.")

        hashed_pwd = hash_password(payload.password)
        new_user = User(
            email=payload.email,
            hashed_password=hashed_pwd,
            full_name=payload.full_name,
            preferred_language=payload.preferred_language,
            role="player",
            is_active=True,
        )
        return self.user_repo.create(new_user)

    def authenticate(self, payload: UserLoginRequest) -> tuple[User, TokenResponse]:
        """Authenticate user with email and password, issuing access and refresh tokens."""
        user = self.user_repo.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is disabled.")

        tokens = self._generate_tokens(user)
        return user, tokens

    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        """Issue new tokens using a valid refresh token."""
        decoded = decode_token(payload.refresh_token, expected_type="refresh")
        user_id_str = decoded.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid refresh token payload.")

        try:
            user_uuid = uuid.UUID(user_id_str)
        except ValueError as err:
            raise UnauthorizedException("Invalid user ID in token.") from err

        user = self.user_repo.get_by_id(user_uuid)
        if user is None or not user.is_active:
            raise UnauthorizedException("User no longer exists or is disabled.")

        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> TokenResponse:
        """Helper to create access and refresh tokens for a user."""
        access_token = create_access_token(user.id, role=user.role)
        refresh_token = create_refresh_token(user.id)
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )
