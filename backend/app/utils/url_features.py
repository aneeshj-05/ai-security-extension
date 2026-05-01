import re
import math
from collections import Counter
from urllib.parse import urlparse
from thefuzz import fuzz
from app.utils.whois_lookup import get_domain_age_days


SUSPICIOUS_KEYWORDS = ["login", "verify", "secure", "account", "update", "banking", "confirm", "signin", "paypal", "ebay"]
SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click", ".link"]
TRUSTED_DOMAINS = ["google.com", "amazon.com", "paypal.com", "facebook.com", "microsoft.com",
                   "apple.com", "netflix.com", "instagram.com", "twitter.com", "linkedin.com"]


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _is_typosquat(hostname: str) -> bool:
    if not hostname:
        return False
    parts = hostname.split(".")
    root_name = parts[-2] if len(parts) >= 2 else parts[0]  # just the name, no TLD

    for trusted in TRUSTED_DOMAINS:
        trusted_name = trusted.split(".")[0]
        similarity = fuzz.ratio(root_name, trusted_name)
        if 60 < similarity < 100:  # similar but not exact
            return True
    return False


def extract_features(url: str) -> dict:
    # auto-add scheme so urlparse can extract hostname correctly
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""

    return {
        # --- existing features ---
        "url_length": len(url),
        "has_https": parsed.scheme == "https",
        "has_ip_address": bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname)),
        "subdomain_count": hostname.count(".") - 1 if hostname.count(".") > 1 else 0,
        "has_at_symbol": "@" in url,
        "has_double_slash_redirect": "//" in path,
        "hyphen_count": hostname.count("-"),
        "special_char_count": len(re.findall(r"[%@!?=&]", url)),
        "suspicious_keyword_count": sum(kw in url.lower() for kw in SUSPICIOUS_KEYWORDS),
        "suspicious_tld": any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS),
        "domain_length": len(hostname),
        "path_depth": path.count("/"),
        # --- new features ---
        "url_entropy": round(_entropy(hostname), 4),
        "is_typosquat": _is_typosquat(hostname),
        "domain_age_days": get_domain_age_days(hostname),
    }
