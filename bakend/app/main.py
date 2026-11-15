"""Main FastAPI application entrypoint for AgroSight Fair Space API."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import check_db_health

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Educational Space Agriculture Game Backend (NASA Space Apps)",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
