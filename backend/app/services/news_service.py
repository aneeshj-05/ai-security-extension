from app.models.loader import get_fake_news_model
from app.utils.text_processing import extract_content_features, normalize_text

HEURISTIC_RULES = [
    (
        "short_body",
        lambda f: f["word_count"] < 100,
        "Article body is very short for a news claim",
        15,
    ),
    (
        "clickbait_title",
        lambda f: f["has_clickbait_title"],
        "Title contains clickbait or sensational wording",
        20,
    ),
    (
        "many_exclamations",
        lambda f: f["exclamation_count"] >= 3,
        "Text uses repeated exclamation marks",
        15,
    ),
    (
        "many_uppercase_words",
        lambda f: f["uppercase_word_count"] >= 5,
        "Text contains many uppercase emphasis words",
        10,
    ),
    (
        "sensational_terms",
        lambda f: f["sensational_term_count"] >= 2,
        "Text repeats sensational or conspiracy-style terms",
        25,
    ),
]


def _heuristic_score(features: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    for rule_id, check, reason, weight in HEURISTIC_RULES:
        if check(features):
            score += weight
            reasons.append(reason)

    return min(score, 100), reasons


def analyze_content(title: str, body_text: str) -> dict:
    content_features = extract_content_features(title, body_text)
    risk_score, reasons = _heuristic_score(content_features)
    model = get_fake_news_model()
    ml_confidence = None
    ml_enabled = model is not None
    ml_model_version = model.version if model else None

    if model:
        try:
            ml_confidence = model.predict_probability(
                normalize_text(title, body_text))
        except Exception:
            model = None
            ml_enabled = False
            ml_model_version = None

    if model:
        is_fake_news = ml_confidence >= model.threshold

        if is_fake_news:
            risk_score = max(risk_score, round(ml_confidence * 100))
            reasons.append("ML model confidence exceeded fake-news threshold")

        verdict = "Likely Fake News" if is_fake_news else "Likely Reliable"
    else:
        is_fake_news = risk_score >= 50
        verdict = (
            "Suspicious Content" if is_fake_news else "Insufficient Fake-News Signals"
        )

    return {
        "is_fake_news": is_fake_news,
        "risk_score": risk_score,
        "verdict": verdict,
        "reasons": reasons,
        "content_features": content_features,
        "ml_confidence": ml_confidence,
        "ml_enabled": ml_enabled,
        "ml_model_version": ml_model_version,
    }
