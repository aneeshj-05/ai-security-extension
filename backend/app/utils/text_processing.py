import re

SENSATIONAL_TERMS = {
    "shocking",
    "miracle",
    "secret",
    "exposed",
    "hoax",
    "conspiracy",
    "unbelievable",
    "urgent",
    "breaking",
    "censored",
}


def normalize_text(title: str, body_text: str) -> str:
    return f"{title.strip()} {body_text.strip()}".strip()


def extract_content_features(title: str, body_text: str) -> dict:
    text = normalize_text(title, body_text)
    words = re.findall(r"[A-Za-z0-9']+", text)
    title_words = re.findall(r"[A-Za-z0-9']+", title)
    lower_words = [word.lower() for word in words]

    sentence_count = max(1, len(re.findall(r"[.!?]+", body_text)))
    uppercase_words = [word for word in words if len(
        word) > 2 and word.isupper()]
    sensational_count = sum(word in SENSATIONAL_TERMS for word in lower_words)

    return {
        "title_length": len(title),
        "body_length": len(body_text),
        "word_count": len(words),
        "sentence_count": sentence_count,
        "avg_sentence_length": round(len(words) / sentence_count, 2),
        "title_word_count": len(title_words),
        "exclamation_count": text.count("!"),
        "question_count": text.count("?"),
        "uppercase_word_count": len(uppercase_words),
        "sensational_term_count": sensational_count,
        "has_clickbait_title": sensational_count > 0 or title.count("!") > 0,
    }
