import asyncio
from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.request import URLRequest
from app.schemas.response import URLAnalysisResponse
from app.services.phishing_service import analyze_url

router = APIRouter()


@router.post("/analyze-url", response_model=URLAnalysisResponse)
async def analyze(request: URLRequest):
    try:
        result = await analyze_url(request.url)
        return URLAnalysisResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_URL", "message": str(exc)},
        ) from exc


@router.post("/analyze-urls-batch", response_model=list[URLAnalysisResponse])
async def analyze_batch(request: list[URLRequest]):
    results = await asyncio.gather(*(analyze_url(item.url) for item in request))
    return [URLAnalysisResponse(**result) for result in results]
