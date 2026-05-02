from pydantic import BaseModel, field_validator
from urllib.parse import urlparse


class URLRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        url = value.strip()

        if not url:
            raise ValueError("URL is required.")

        if not url.startswith(("http://", "https://")):
            raise ValueError("Only http and https URLs can be analyzed.")

        parsed = urlparse(url)
        if not parsed.hostname:
            raise ValueError("Malformed URL. A hostname is required.")

        return url


class ContentAnalysisRequest(BaseModel):
    title: str = ""
    body_text: str
    source_url: str = ""

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("body_text")
    @classmethod
    def validate_body_text(cls, value: str) -> str:
        text = value.strip()

        if not text:
            raise ValueError("Body text is required.")

        if len(text.split()) < 20:
            raise ValueError("Body text must contain at least 20 words.")

        return text
