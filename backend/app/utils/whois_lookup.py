import asyncio
import socket
import whois
from datetime import datetime
from functools import lru_cache
from app.core.config import get_settings

UNKNOWN_WHOIS_RESULT = {
    "age_days": -1,
    "status": "unknown",
    "domain_resolves": None,
}


def _clean_hostname(hostname: str) -> str:
    return hostname.strip().lower().rstrip(".")


def _dns_resolves(hostname: str) -> bool:
    try:
        socket.getaddrinfo(hostname, None)
        return True
    except OSError:
        return False


@lru_cache(maxsize=4096)
def _lookup_domain_age_days(hostname: str) -> dict:
    hostname = _clean_hostname(hostname)

    if not hostname:
        return {
            **UNKNOWN_WHOIS_RESULT,
            "status": "invalid_hostname",
            "domain_resolves": False,
        }

    try:
        w = whois.whois(hostname)
        created = w.creation_date
        if isinstance(created, list):
            created = next(
                (item for item in created if item is not None), None)
        if created is None:
            return {
                "age_days": -1,
                "status": "creation_date_missing",
                "domain_resolves": _dns_resolves(hostname),
            }
        return {
            "age_days": max(0, (datetime.now() - created).days),
            "status": "whois_ok",
            "domain_resolves": True,
        }
    except Exception as exc:
        resolves = _dns_resolves(hostname)
        return {
            "age_days": -1,
            "status": f"whois_failed:{type(exc).__name__}",
            "domain_resolves": resolves,
        }


async def get_domain_age_days(hostname: str) -> dict:
    settings = get_settings()
    hostname = _clean_hostname(hostname)

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_lookup_domain_age_days, hostname),
            timeout=settings.whois_timeout_seconds,
        )
    except asyncio.TimeoutError:
        return {
            "age_days": -1,
            "status": "whois_timeout",
            "domain_resolves": await asyncio.to_thread(_dns_resolves, hostname),
        }
    except Exception as exc:
        return {
            "age_days": -1,
            "status": f"lookup_failed:{type(exc).__name__}",
            "domain_resolves": await asyncio.to_thread(_dns_resolves, hostname),
        }
