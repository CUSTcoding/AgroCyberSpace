"""Main FastAPI application entrypoint for AgroSight Fair Space API."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_db_health
from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.earth_observation.router import router as earth_observation_router
from app.modules.game.router import content_router
from app.modules.game.router import router as game_router
from app.modules.regions.router import router as regions_router
from app.modules.users.router import router as users_router
from app.shared.exceptions import AppException

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Educational Space Agriculture Game Backend (NASA Space Apps)",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)


# Standard error handler for domain exceptions
@app.exception_handler(AppException)
def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Format domain exceptions according to standard error schema."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


# Standard error handler for validation errors
@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Format Pydantic validation errors according to standard error schema."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": exc.errors(),
            }
        },
    )


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(regions_router, prefix=settings.API_V1_PREFIX)
app.include_router(game_router, prefix=settings.API_V1_PREFIX)
app.include_router(content_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
app.include_router(earth_observation_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root status endpoint."""
    return {"name": settings.PROJECT_NAME, "status": "running", "version": settings.VERSION}


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["Health"])
def health_check(response: Response) -> dict[str, Any]:
    """Comprehensive health check for API, cloud database, and PostGIS."""
    db_result = check_db_health(retries=2, retry_delay_seconds=0.5)

    is_db_configured = db_result["status"] != "not_configured"
    is_db_healthy = db_result["status"] == "ok"

    if is_db_configured and not is_db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = "unhealthy"
    elif not is_db_configured:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "status": overall_status,
        "api": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "database": {
            "status": db_result["status"],
            "latency_ms": db_result["latency_ms"],
            "error": db_result["error"],
        },
        "postgis": {
            "installed": db_result["postgis_installed"],
            "version": db_result["postgis_version"],
        },
    }
