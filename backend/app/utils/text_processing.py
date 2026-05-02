import re

SENSATIONAL_TERMS = {
    # Original
    "shocking", "miracle", "secret", "exposed", "hoax",
    "conspiracy", "unbelievable", "urgent", "breaking", "censored",
    # Expanded — misinformation / clickbait
    "bombshell", "explosive", "outrage", "scandalous", "alarming",
    "terrifying", "devastating", "horrifying", "disgusting", "insane",
    "incredible", "unreal", "jaw-dropping", "mind-blowing", "stunning",
    "leaked", "banned", "suppressed", "silenced", "coverup",
    "truth", "hidden", "revealed", "proof", "confirmed",
    "mainstream", "propaganda", "corrupt", "rigged", "stolen",
    # Satire / absurdist markers
    "report", "sources", "officials", "experts", "scientists",
    "nation", "area man", "local man", "local woman",
}

CLICKBAIT_PATTERNS = [
    r"\d+ (things|reasons|ways|facts|signs|tips|tricks)",
    r"you (won't|will never|need to|should|must|have to)",
    r"(what|why|how) (nobody|no one|everyone|they) (tells?|knows?|wants?|says?)",
    r"(this|the) (one|single) (weird|simple|secret|shocking)",
    r"(is|are) (back|gone|dead|over|finished|doomed)",
    r"(just|already) (happened|confirmed|announced|revealed|admitted)",
    r"(breaking|alert|update|developing)[:,]?",
    r"(man|woman|person|guy|kid|child) (who|that) (did|does|said|says|found|discovered)",
    r"(report(s|ed)?|sources? (say|confirm|reveal))",
    r"(nation|country|world|everyone|america) (reacts?|responds?|shocked|stunned|outraged)",
]


def normalize_text(title: str, body_text: str) -> str:
    return f"{title.strip()} {body_text.strip()}".strip()


def _has_clickbait_title(title: str, sensational_count: int) -> bool:
    if sensational_count > 0 or title.count("!") > 0:
        return True
    title_lower = title.lower()
    return any(re.search(p, title_lower) for p in CLICKBAIT_PATTERNS)


def extract_content_features(title: str, body_text: str) -> dict:
    text = normalize_text(title, body_text)
    words = re.findall(r"[A-Za-z0-9']+", text)
    title_words = re.findall(r"[A-Za-z0-9']+", title)
    lower_words = [word.lower() for word in words]
    body_lower = body_text.lower()

    sentence_count = max(1, len(re.findall(r"[.!?]+", body_text)))
    uppercase_words = [word for word in words if len(word) > 2 and word.isupper()]
    sensational_count = sum(word in SENSATIONAL_TERMS for word in lower_words)
    clickbait_pattern_count = sum(
        1 for p in CLICKBAIT_PATTERNS if re.search(p, body_lower)
    )
    has_clickbait = _has_clickbait_title(title, sensational_count)

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
        "clickbait_pattern_count": clickbait_pattern_count,
        "has_clickbait_title": has_clickbait,
    }
