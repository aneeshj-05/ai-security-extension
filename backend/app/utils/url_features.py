import re
import math
from collections import Counter
from urllib.parse import urlparse
from thefuzz import fuzz
from app.core.config import get_settings
from app.utils.whois_lookup import get_domain_age_days

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "banking", "confirm",
    "signin", "paypal", "ebay", "apple", "microsoft", "google", "netflix",
    "amazon", "billing", "support", "portal", "security", "customer", "service"
]
SUSPICIOUS_TLDS = [
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click", ".link",
    ".info", ".biz", ".icu", ".online", ".site", ".work"
]
UNKNOWN_DOMAIN_AGE_DAYS = -1


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _normalize(text: str) -> str:
    replacements = {'0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '8': 'b'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _is_typosquat(hostname: str) -> bool:
    if not hostname:
        return False

    parts = hostname.split(".")
    # just the name, no TLD
    root_name = parts[-2] if len(parts) >= 2 else parts[0]
    settings = get_settings()

    normalized_root = _normalize(root_name)

    for trusted_name in settings.trusted_domain_roots:
        if root_name == trusted_name:
            continue

        if abs(len(root_name) - len(trusted_name)) > 3:
            continue

        similarity = fuzz.ratio(normalized_root, trusted_name)
        raw_similarity = fuzz.ratio(root_name, trusted_name)
        
        if similarity >= 80 or raw_similarity >= 80:
            return True
            
    return False


def extract_lexical_features(
    url: str, domain_age_days: int = UNKNOWN_DOMAIN_AGE_DAYS
) -> dict:
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
        "suspicious_keyword_count": sum(
            kw in url.lower() for kw in SUSPICIOUS_KEYWORDS
        ),
        "suspicious_tld": any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS),
        "domain_length": len(hostname),
        "path_depth": path.count("/"),
        # --- new features ---
        "url_entropy": round(_entropy(hostname), 4),
        "is_typosquat": _is_typosquat(hostname),
        "domain_age_days": domain_age_days,
    }


async def extract_features(url: str, include_whois: bool = True) -> dict:
    features = extract_lexical_features(url)

    if include_whois:
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            features["domain_age_status"] = "invalid_hostname"
            features["domain_resolves"] = False
        else:
            whois_result = await get_domain_age_days(hostname)
            features["domain_age_days"] = whois_result["age_days"]
            features["domain_age_status"] = whois_result["status"]
            features["domain_resolves"] = whois_result["domain_resolves"]
    else:
        features["domain_age_status"] = "skipped"
        features["domain_resolves"] = None

    return features
