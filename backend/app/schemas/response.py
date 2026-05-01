from pydantic import BaseModel
from typing import List, Dict, Any


class URLAnalysisResponse(BaseModel):
    url: str
    is_phishing: bool
    risk_score: int
    verdict: str
    reasons: List[str]
    features: Dict[str, Any]
