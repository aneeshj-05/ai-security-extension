import os
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _extract_domain_from_line(line: str) -> str:
    value = line.strip().lower()

    if not value or value.startswith("#"):
        return ""

    # Supports plain lists (`example.com`) and CSV rows (`1,example.com`).
    parts = [part.strip() for part in value.split(",") if part.strip()]
    candidate = parts[-1] if parts else value

    if candidate.startswith(("http://", "https://")):
        candidate = candidate.split("://", 1)[1]

    domain = candidate.split("/", 1)[0].lstrip(".")
    return "" if domain in {"domain", "url", "hostname"} else domain


def _domain_root(domain: str) -> str:
    parts = domain.split(".")
    return parts[-2] if len(parts) >= 2 else parts[0]


def _load_trusted_domains(path: Path, limit: int) -> list[str]:
    if not path.exists():
        return []

    domains = []
    for line in path.read_text().splitlines():
        domain = _extract_domain_from_line(line)
        if domain:
            domains.append(domain)

        if limit and len(domains) >= limit:
            break

    return domains


class Settings:
    def __init__(self) -> None:
        extension_id = os.getenv("CHROME_EXTENSION_ID", "").strip()
        allowed_origins = os.getenv("AI_SECURITY_ALLOWED_ORIGINS", "").strip()

        if allowed_origins:
            self.allowed_origins = _split_csv(allowed_origins)
        elif extension_id:
            self.allowed_origins = [f"chrome-extension://{extension_id}"]
        else:
            self.allowed_origins = [
                "chrome-extension://replace-with-your-extension-id"]

        self.whois_timeout_seconds = float(
            os.getenv("WHOIS_TIMEOUT_SECONDS", "3"))
        self.phishing_ml_threshold = float(
            os.getenv("PHISHING_ML_THRESHOLD", "0.8"))
        self.phishing_model_path = os.getenv(
            "PHISHING_MODEL_PATH",
            str(BASE_DIR.parents[1] / "ml_models" / "phishing" / "model.pkl"),
        )
        self.fake_news_ml_threshold = float(
            os.getenv("FAKE_NEWS_ML_THRESHOLD", "0.75"))
        self.fake_news_model_path = os.getenv(
            "FAKE_NEWS_MODEL_PATH",
            str(BASE_DIR.parents[1] / "ml_models" / "fake_news" / "model.pkl"),
        )

        trusted_domains_file = os.getenv(
            "TRUSTED_DOMAINS_FILE",
            str(BASE_DIR / "data" / "trusted_domains.txt"),
        )
        self.trusted_domains_limit = int(
            os.getenv("TRUSTED_DOMAINS_LIMIT", "10000"))
        self.trusted_domains = sorted(
            set(
                _load_trusted_domains(
                    Path(trusted_domains_file), self.trusted_domains_limit
                )
            )
        )
        self.trusted_domain_roots = sorted(
            {_domain_root(domain) for domain in self.trusted_domains if domain}
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
