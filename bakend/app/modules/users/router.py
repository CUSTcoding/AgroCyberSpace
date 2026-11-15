"""Users management API router."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser, RequireAdmin
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserResponse, UserUpdateRequest
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    """Dependency injecting UserService with UserRepository."""
    user_repo = UserRepository(db)
    return UserService(user_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
def get_current_user_profile(current_user: CurrentUser) -> UserResponse:
    """Retrieve profile of currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
def update_current_user_profile(
    payload: UserUpdateRequest,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> UserResponse:
    """Update profile details for currently authenticated user."""
    updated = service.update_profile(current_user, payload)
    return UserResponse.model_validate(updated)


@router.get(
    "/admin/ping",
    status_code=status.HTTP_200_OK,
    summary="Admin role check endpoint",
)
def admin_only_ping(admin_user: RequireAdmin) -> dict[str, str]:
    """Test endpoint verifying administrator authorization."""
    return {"status": "ok", "admin_email": admin_user.email}
