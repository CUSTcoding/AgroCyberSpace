"""Schemas for privacy-conscious template explanations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExplanationContext(BaseModel):
    """Allow-listed scientific context; personal fields are rejected."""

    model_config = ConfigDict(extra="forbid")

    category: Literal["observed", "derived", "forecast", "simulation"]
    source: str = Field(min_length=1, max_length=120)
    dataset_version: str = Field(min_length=1, max_length=80)
    limitations: list[str] = Field(default_factory=list, max_length=10)
    resolution_warning: str | None = Field(default=None, max_length=300)


class ExplainRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context: ExplanationContext
    language: Literal["pt", "en"] = "pt"


class ExplainResponse(BaseModel):
    message_simple: str
    audio_text: str
    why: str
    limitations: list[str]
    technical_details: dict[str, str]


class AIHealthResponse(BaseModel):
    status: Literal["ok"]
    provider: Literal["template"]
    external_service: Literal[False]
