from urllib.parse import urlparse
from app.models.loader import get_phishing_model
from app.utils.url_features import extract_features
from app.core.config import get_settings

RULES = [
    # --- existing rules ---
    (
        "has_ip_address",
        lambda f: f["has_ip_address"],
        "IP address used instead of domain",
        30,
    ),
    (
        "no_https",
        lambda f: not f["has_https"],
        "No HTTPS — connection is not secure",
        20,
    ),
    ("has_at_symbol", lambda f: f["has_at_symbol"],
     "URL contains '@' symbol", 20),
    ("long_url", lambda f: f["url_length"] > 75, "Unusually long URL", 10),
    ("many_subdomains", lambda f: f["subdomain_count"]
     > 2, "Excessive subdomains", 15),
    (
        "double_slash_redirect",
        lambda f: f["has_double_slash_redirect"],
        "Double slash redirect in path",
        15,
    ),
    ("many_hyphens", lambda f: f["hyphen_count"]
     > 2, "Too many hyphens in domain", 10),
    (
        "suspicious_keywords",
        lambda f: f["suspicious_keyword_count"] >= 2,
        "Multiple phishing-related keywords",
        20,
    ),
    (
        "suspicious_tld",
        lambda f: f["suspicious_tld"],
        "Suspicious top-level domain",
        25,
    ),
    (
        "high_special_chars",
        lambda f: f["special_char_count"] > 5,
        "High number of special characters",
        10,
    ),
    # --- new rules ---
    (
        "high_entropy",
        lambda f: f["url_entropy"] > 3.5,
        "Domain looks randomly generated (high entropy)",
        20,
    ),
    (
        "typosquat",
        lambda f: f["is_typosquat"],
        "Domain closely resembles a trusted brand (typosquatting)",
        35,
    ),
    (
        "new_domain",
        lambda f: 0 < f["domain_age_days"] < 180,
        "Domain is less than 6 months old",
        25,
    ),
]


def _rule_score(features: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    for rule_id, check, reason, weight in RULES:
        if check(features):
            score += weight
            reasons.append(reason)

    return min(score, 100), reasons


def _is_trusted_domain(hostname: str) -> bool:
    if not hostname:
        return False
    hostname = hostname.lower()
    settings = get_settings()
    for trusted in settings.trusted_domains:
        if hostname == trusted or hostname.endswith("." + trusted):
            return True
    return False


async def analyze_url(url: str) -> dict:
    features = await extract_features(url)
    model = get_phishing_model()
    ml_confidence = None
    ml_enabled = model is not None
    ml_model_version = model.version if model else None

    # Normalization for hostname check
    normalized_url = url if url.startswith(("http://", "https://")) else "http://" + url
    hostname = urlparse(normalized_url).hostname or ""

    # Short-circuit for highly trusted domains to prevent false positives
    # (e.g. extremely long Google search URLs with special characters)
    if _is_trusted_domain(hostname):
        return {
            "url": url,
            "is_phishing": False,
            "risk_score": 0,
            "verdict": "Safe",
            "reasons": ["Domain is explicitly trusted and known to be safe"],
            "features": features,
            "ml_confidence": None,
            "ml_enabled": ml_enabled,
            "ml_model_version": ml_model_version,
        }

    risk_score, reasons = _rule_score(features)

    if model:
        try:
            ml_confidence = model.predict_probability(features)
        except Exception:
            model = None
            ml_enabled = False
            ml_model_version = None

    # typosquatting is an instant flag — score doesn't matter
    if features["is_typosquat"]:
        return {
            "url": url,
            "is_phishing": True,
            "risk_score": 100,
            "verdict": "Invalid — Typosquat Domain",
            "reasons": reasons,
            "features": features,
            "ml_confidence": None,
            "ml_enabled": ml_enabled,
            "ml_model_version": ml_model_version,
        }

    if model:
        ml_is_phishing = ml_confidence >= model.threshold
        rule_is_phishing = risk_score >= 40
        is_phishing = ml_is_phishing or rule_is_phishing

        if ml_is_phishing:
            risk_score = max(risk_score, round(ml_confidence * 100))
            reasons.append("ML model confidence exceeded phishing threshold")

        verdict = "Phishing" if is_phishing else "Safe"
    else:
        is_phishing = risk_score >= 30
        verdict = "Phishing" if is_phishing else "Safe"

    return {
        "url": url,
        "is_phishing": is_phishing,
        "risk_score": risk_score,
        "verdict": verdict,
        "reasons": reasons,
        "features": features,
        "ml_confidence": ml_confidence,
        "ml_enabled": ml_enabled,
        "ml_model_version": ml_model_version,
    }
