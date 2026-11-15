"""Authentication API router."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import (
    AuthResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    """Dependency injecting AuthService with UserRepository."""
    user_repo = UserRepository(db)
    return AuthService(user_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new player",
)
def register(
    payload: UserRegisterRequest,
    service: AuthServiceDep,
) -> UserResponse:
    """Register a new player account in the AgroSight system."""
    user = service.register(payload)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User credentials login",
)
def login(
    payload: UserLoginRequest,
    service: AuthServiceDep,
) -> AuthResponse:
    """Authenticate with email and password, returning tokens and profile."""
    user, tokens = service.authenticate(payload)
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
def refresh_token(
    payload: RefreshTokenRequest,
    service: AuthServiceDep,
) -> TokenResponse:
    """Exchange a valid refresh token for a new set of JWT access and refresh tokens."""
    return service.refresh(payload)
