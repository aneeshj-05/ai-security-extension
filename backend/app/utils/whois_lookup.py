import whois
from datetime import datetime


def get_domain_age_days(hostname: str) -> int:
    try:
        w = whois.whois(hostname)
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        if created is None:
            return -1
        return (datetime.now() - created).days
    except Exception:
        return -1  # unknown / lookup failed
