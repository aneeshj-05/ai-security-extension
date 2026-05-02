from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.fake_news import router as fake_news_router
from app.api.phishing import router as phishing_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="AI Security Extension API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(phishing_router, prefix="/api/v1", tags=["Phishing"])
app.include_router(fake_news_router, prefix="/api/v1", tags=["Fake News"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "INVALID_REQUEST",
                "message": "Request validation failed.",
                "errors": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
