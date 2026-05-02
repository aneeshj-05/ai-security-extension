import asyncio

from pydantic import ValidationError
from app.services import phishing_service
from app.services import news_service
from app.schemas.request import ContentAnalysisRequest
from ml_models.phishing.features import FEATURE_COLUMNS, features_to_vector
from ml_models.phishing.train import normalize_label


def test_feature_vector_order_and_conversion():
    features = {
        "url_length": 20,
        "has_https": True,
        "has_ip_address": False,
        "subdomain_count": 1,
        "has_at_symbol": False,
        "has_double_slash_redirect": False,
        "hyphen_count": 2,
        "special_char_count": 3,
        "suspicious_keyword_count": 1,
        "suspicious_tld": True,
        "domain_length": 11,
        "path_depth": 2,
        "url_entropy": 3.2,
        "is_typosquat": False,
        "domain_age_days": -1,
    }

    vector = features_to_vector(features)

    assert len(vector) == len(FEATURE_COLUMNS)
    assert vector[FEATURE_COLUMNS.index("has_https")] == 1.0
    assert vector[FEATURE_COLUMNS.index("has_ip_address")] == 0.0
    assert vector[FEATURE_COLUMNS.index("domain_age_days")] == -1.0


def test_invalid_label_is_rejected():
    try:
        normalize_label("malware")
    except ValueError as exc:
        assert "Unsupported label" in str(exc)
    else:
        raise AssertionError("Expected invalid label to raise ValueError")


def test_missing_model_falls_back_to_rule_score(monkeypatch):
    async def fake_extract_features(url):
        return {
            "has_ip_address": False,
            "has_https": True,
            "has_at_symbol": False,
            "url_length": 20,
            "subdomain_count": 0,
            "has_double_slash_redirect": False,
            "hyphen_count": 0,
            "suspicious_keyword_count": 0,
            "suspicious_tld": False,
            "special_char_count": 0,
            "url_entropy": 2.0,
            "is_typosquat": False,
            "domain_age_days": -1,
        }

    monkeypatch.setattr(phishing_service, "extract_features", fake_extract_features)
    monkeypatch.setattr(phishing_service, "get_phishing_model", lambda: None)

    result = asyncio.run(phishing_service.analyze_url("https://example.com"))

    assert result["is_phishing"] is False
    assert result["ml_enabled"] is False
    assert result["ml_confidence"] is None


def test_high_ml_probability_flags_phishing(monkeypatch):
    class FakeModel:
        threshold = 0.8
        version = "test-model"

        def predict_probability(self, features):
            return 0.91

    async def fake_extract_features(url):
        return {
            "has_ip_address": False,
            "has_https": True,
            "has_at_symbol": False,
            "url_length": 20,
            "subdomain_count": 0,
            "has_double_slash_redirect": False,
            "hyphen_count": 0,
            "suspicious_keyword_count": 0,
            "suspicious_tld": False,
            "special_char_count": 0,
            "url_entropy": 2.0,
            "is_typosquat": False,
            "domain_age_days": -1,
        }

    monkeypatch.setattr(phishing_service, "extract_features", fake_extract_features)
    monkeypatch.setattr(phishing_service, "get_phishing_model", lambda: FakeModel())

    result = asyncio.run(phishing_service.analyze_url("https://some-unknown-domain.xyz"))

    assert result["is_phishing"] is True
    assert result["risk_score"] == 91
    assert result["ml_confidence"] == 0.91
    assert result["ml_enabled"] is True


def test_typosquat_wins_even_with_low_ml_probability(monkeypatch):
    class FakeModel:
        threshold = 0.8
        version = "test-model"

        def predict_probability(self, features):
            return 0.1

    async def fake_extract_features(url):
        return {
            "has_ip_address": False,
            "has_https": True,
            "has_at_symbol": False,
            "url_length": 20,
            "subdomain_count": 0,
            "has_double_slash_redirect": False,
            "hyphen_count": 0,
            "suspicious_keyword_count": 0,
            "suspicious_tld": False,
            "special_char_count": 0,
            "url_entropy": 2.0,
            "is_typosquat": True,
            "domain_age_days": -1,
        }

    monkeypatch.setattr(phishing_service, "extract_features", fake_extract_features)
    monkeypatch.setattr(phishing_service, "get_phishing_model", lambda: FakeModel())

    result = asyncio.run(phishing_service.analyze_url("https://googIe.com"))

    assert result["is_phishing"] is True
    assert result["verdict"] == "Invalid — Typosquat Domain"
    assert result["ml_confidence"] is None


def test_content_request_rejects_short_body():
    try:
        ContentAnalysisRequest(title="Short", body_text="too short")
    except ValidationError as exc:
        assert "at least 20 words" in str(exc)
    else:
        raise AssertionError("Expected short content body to fail validation")


def test_fake_news_falls_back_to_heuristics(monkeypatch):
    monkeypatch.setattr(news_service, "get_fake_news_model", lambda: None)

    result = news_service.analyze_content(
        "SHOCKING secret exposed!",
        (
            "Breaking shocking secret exposed conspiracy claims are repeated again "
            "and again with urgent language but without careful detail or reliable "
            "context for readers to evaluate the story properly."
        ),
    )

    assert result["ml_enabled"] is False
    assert result["ml_confidence"] is None
    assert result["risk_score"] > 0
    assert result["reasons"]


def test_fake_news_model_confidence_flags_content(monkeypatch):
    class FakeNewsModel:
        threshold = 0.75
        version = "fake-news-test"

        def predict_probability(self, text):
            return 0.88

    monkeypatch.setattr(news_service, "get_fake_news_model", lambda: FakeNewsModel())

    result = news_service.analyze_content(
        "Routine title",
        (
            "This article contains enough body text to pass validation and allow "
            "the fake news model branch to evaluate the content through a mocked "
            "classifier response during the backend service test."
        ),
    )

    assert result["is_fake_news"] is True
    assert result["ml_enabled"] is True
    assert result["ml_confidence"] == 0.88
    assert result["ml_model_version"] == "fake-news-test"
