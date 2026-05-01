from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.phishing import router as phishing_router

app = FastAPI(title="AI Security Extension API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(phishing_router, prefix="/api/v1", tags=["Phishing"])


@app.get("/health")
def health():
    return {"status": "ok"}
