"""Main FastAPI application entrypoint for AgroSight API."""

from fastapi import FastAPI

app = FastAPI(
    title="AgroSight Fair Space API",
    description="Educational Space Agriculture Game Backend",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root status endpoint."""
    return {"name": "AgroSight Fair Space API", "status": "running"}
