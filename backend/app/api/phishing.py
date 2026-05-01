from fastapi import APIRouter
from app.schemas.request import URLRequest
from app.schemas.response import URLAnalysisResponse
from app.services.phishing_service import analyze_url

router = APIRouter()


@router.post("/analyze-url", response_model=URLAnalysisResponse)
def analyze(request: URLRequest):
    result = analyze_url(request.url)
    return URLAnalysisResponse(**result)
