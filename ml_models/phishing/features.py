FEATURE_COLUMNS = [
    "url_length",
    "has_https",
    "has_ip_address",
    "subdomain_count",
    "has_at_symbol",
    "has_double_slash_redirect",
    "hyphen_count",
    "special_char_count",
    "suspicious_keyword_count",
    "suspicious_tld",
    "domain_length",
    "path_depth",
    "url_entropy",
    "is_typosquat",
    "domain_age_days",
]


def _to_float(value) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0

    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def features_to_vector(features: dict) -> list[float]:
    vector = []

    for column in FEATURE_COLUMNS:
        value = features.get(column)

        if column == "domain_age_days" and value in (None, ""):
            value = -1

        vector.append(_to_float(value))

    return vector
