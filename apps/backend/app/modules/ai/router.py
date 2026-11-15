"""Template-only AI explanation endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.ai.schemas import AIHealthResponse, ExplainRequest, ExplainResponse
from app.modules.ai.service import TemplateProvider

router = APIRouter(prefix="/ai", tags=["AI"])
provider = TemplateProvider()


@router.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest) -> ExplainResponse:
    """Explain structured data context using deterministic templates."""
    return provider.explain(request)


@router.post("/hint", response_model=ExplainResponse)
def hint(request: ExplainRequest) -> ExplainResponse:
    """Provide a field-observation hint using deterministic templates."""
    return provider.hint(request)


@router.get("/health", response_model=AIHealthResponse)
def health() -> AIHealthResponse:
    """Report the active local explanation provider."""
    return AIHealthResponse(status="ok", provider="template", external_service=False)
