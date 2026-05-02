from fastapi import APIRouter
from app.schemas.request import ContentAnalysisRequest
from app.schemas.response import ContentAnalysisResponse
from app.services.news_service import analyze_content

router = APIRouter()


@router.post("/analyze-content", response_model=ContentAnalysisResponse)
def analyze(request: ContentAnalysisRequest):
    result = analyze_content(request.title, request.body_text, request.source_url)
    return ContentAnalysisResponse(**result)
