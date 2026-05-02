from pydantic import BaseModel
from typing import Any


class URLAnalysisResponse(BaseModel):
    url: str
    is_phishing: bool
    risk_score: int
    verdict: str
    reasons: list[str]
    features: dict[str, Any]
    ml_confidence: float | None = None
    ml_enabled: bool = False
    ml_model_version: str | None = None


class ContentAnalysisResponse(BaseModel):
    is_fake_news: bool
    risk_score: int
    verdict: str
    reasons: list[str]
    content_features: dict[str, Any]
    ml_confidence: float | None = None
    ml_enabled: bool = False
    ml_model_version: str | None = None
