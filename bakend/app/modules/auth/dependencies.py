"""FastAPI authentication and authorization dependencies."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.shared.exceptions import ForbiddenException, UnauthorizedException

http_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Validate JWT access token and return currently authenticated user."""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("Authentication token is missing.")

    payload = decode_token(credentials.credentials, expected_type="access")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload: missing subject claim.")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError as err:
        raise UnauthorizedException("Invalid user ID in token.") from err

    repo = UserRepository(db)
    user = repo.get_by_id(user_uuid)
    if user is None:
        raise UnauthorizedException("User associated with token not found.")

    if not user.is_active:
        raise UnauthorizedException("User account is disabled.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """Dependency factory checking that current user has one of the required roles."""

    def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Action requires one of the following roles: {', '.join(allowed_roles)}."
            )
        return current_user

    return role_checker


RequireAdmin = Annotated[User, Depends(require_role("admin"))]
