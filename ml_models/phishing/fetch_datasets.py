import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "datasets" / "phishing" / "raw"
PROCESSED_FILE = BASE_DIR / "datasets" / "phishing" / "processed" / "phishing_urls.csv"

# ── Sources ───────────────────────────────────────────────────────────────────
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"
OPENPHISH_URL = "https://openphish.com/feed.txt"

HEADERS = {"User-Agent": "AI-Security-Extension/1.0 (research project)"}


def setup_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)


def fetch_benign_urls(sample_size: int) -> pd.DataFrame:
    """Download Tranco top-1M list and return the top `sample_size` as benign."""
    print("Fetching Tranco Top-1M (benign)…")
    response = requests.get(TRANCO_URL, headers=HEADERS, timeout=60)
    response.raise_for_status()

    # Save raw zip for reproducibility
    raw_zip = RAW_DIR / "tranco_top1m.csv.zip"
    raw_zip.write_bytes(response.content)
    print(f"  Saved raw zip → {raw_zip}")

    import random
    benign_paths = [
        "", "", "", "", "/", "/index.html", "/about", "/contact-us",
        "/login", "/register", "/search?q=query+string",
        "/docs/api/v1/reference", "/stable/modules/generated/page.html",
        "/category/items?id=123&sort=desc",
        "/wp-content/uploads/image.png",
        "/user/profile?session=abcdef123456",
        "/article/2023/10/05/breaking-news",
        "/?p=123", "/#section"
    ]
    random.seed(42)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open("top-1m.csv") as f:
            df = pd.read_csv(f, names=["rank", "url"], nrows=sample_size)

    def generate_url(domain):
        domain = str(domain).strip()
        path = random.choice(benign_paths)
        return f"https://{domain}{path}"

    df["url"] = df["url"].apply(generate_url)
    df["label"] = 0
    print(f"  {len(df):,} benign URLs collected.")
    return df[["url", "label"]]


def fetch_phishing_urls() -> pd.DataFrame:
    """Download OpenPhish free feed and return all live phishing URLs."""
    print("Fetching OpenPhish feed (phishing)…")
    response = requests.get(OPENPHISH_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    # Save raw feed
    raw_feed = RAW_DIR / "openphish_feed.txt"
    raw_feed.write_text(response.text, encoding="utf-8")
    print(f"  Saved raw feed → {raw_feed}")

    urls = [line.strip() for line in response.text.splitlines() if line.strip().startswith("http")]
    print(f"  {len(urls):,} phishing URLs collected.")

    df = pd.DataFrame({"url": urls, "label": 1})
    return df


def main() -> None:
    setup_dirs()

    try:
        phishing_df = fetch_phishing_urls()
    except Exception as exc:
        print(f"  OpenPhish fetch failed: {exc}")
        # Fall back to cached raw file if it exists
        raw_feed = RAW_DIR / "openphish_feed.txt"
        if raw_feed.exists():
            print("  Using cached OpenPhish feed.")
            urls = [l.strip() for l in raw_feed.read_text().splitlines() if l.strip().startswith("http")]
            phishing_df = pd.DataFrame({"url": urls, "label": 1})
        else:
            print("  No cached feed found. Aborting.")
            raise

    # Balance: match benign count to phishing count
    sample_size = len(phishing_df)
    print(f"Balancing dataset: {sample_size:,} URLs per class.")

    benign_df = fetch_benign_urls(sample_size)

    final_df = (
        pd.concat([benign_df, phishing_df])
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )

    final_df.to_csv(PROCESSED_FILE, index=False)
    print(f"\n✓ Saved {len(final_df):,} rows → {PROCESSED_FILE}")
    print(f"  Phishing: {final_df['label'].sum():,}  |  Benign: {(final_df['label'] == 0).sum():,}")


if __name__ == "__main__":
    main()