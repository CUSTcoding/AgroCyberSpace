"""Application exception definitions matching the AgroSight API contract."""

from __future__ import annotations

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class UnauthorizedException(AppException):
    """HTTP 401 Unauthorized exception."""

    def __init__(
        self,
        message: str = "Invalid credentials or unauthorized access.",
        details: Any = None,
    ) -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
            details=details,
        )


class ForbiddenException(AppException):
    """HTTP 403 Forbidden exception."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        details: Any = None,
    ) -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
            details=details,
        )


class NotFoundException(AppException):
    """HTTP 404 Not Found exception."""

    def __init__(
        self,
        message: str = "Resource not found.",
        details: Any = None,
    ) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
            details=details,
        )


class ConflictException(AppException):
    """HTTP 409 Conflict exception."""

    def __init__(
        self,
        message: str = "Resource conflict occurred.",
        details: Any = None,
    ) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )
