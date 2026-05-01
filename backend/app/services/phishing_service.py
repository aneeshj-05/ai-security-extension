from app.utils.url_features import extract_features


RULES = [
    # --- existing rules ---
    ("has_ip_address",        lambda f: f["has_ip_address"],               "IP address used instead of domain",          30),
    ("no_https",              lambda f: not f["has_https"],                 "No HTTPS — connection is not secure",         20),
    ("has_at_symbol",         lambda f: f["has_at_symbol"],                 "URL contains '@' symbol",                    20),
    ("long_url",              lambda f: f["url_length"] > 75,               "Unusually long URL",                         10),
    ("many_subdomains",       lambda f: f["subdomain_count"] > 2,           "Excessive subdomains",                       15),
    ("double_slash_redirect", lambda f: f["has_double_slash_redirect"],     "Double slash redirect in path",              15),
    ("many_hyphens",          lambda f: f["hyphen_count"] > 2,              "Too many hyphens in domain",                 10),
    ("suspicious_keywords",   lambda f: f["suspicious_keyword_count"] >= 2, "Multiple phishing-related keywords",         20),
    ("suspicious_tld",        lambda f: f["suspicious_tld"],                "Suspicious top-level domain",                25),
    ("high_special_chars",    lambda f: f["special_char_count"] > 5,        "High number of special characters",          10),
    # --- new rules ---
    ("high_entropy",          lambda f: f["url_entropy"] > 3.5,             "Domain looks randomly generated (high entropy)", 20),
    ("typosquat",             lambda f: f["is_typosquat"],                  "Domain closely resembles a trusted brand (typosquatting)", 35),
    ("new_domain",            lambda f: 0 < f["domain_age_days"] < 180,     "Domain is less than 6 months old",           25),
]


def analyze_url(url: str) -> dict:
    features = extract_features(url)
    score = 0
    reasons = []

    for rule_id, check, reason, weight in RULES:
        if check(features):
            score += weight
            reasons.append(reason)

    risk_score = min(score, 100)

    # typosquatting is an instant flag — score doesn't matter
    if features["is_typosquat"]:
        return {
            "url": url,
            "is_phishing": True,
            "risk_score": risk_score,
            "verdict": "Invalid — Typosquat Domain",
            "reasons": reasons,
            "features": features,
        }

    is_phishing = risk_score >= 30

    return {
        "url": url,
        "is_phishing": is_phishing,
        "risk_score": risk_score,
        "verdict": "Phishing" if is_phishing else "Safe",
        "reasons": reasons,
        "features": features,
    }
