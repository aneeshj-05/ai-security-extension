import io
from pathlib import Path

import pandas as pd
import requests

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "datasets" / "fake_news" / "raw"

# ── Source: WELFake dataset hosted on Zenodo (no auth required) ───────────────
# WELFake: ~72k articles, columns — title, text, label (0=Fake, 1=Real)
ZENODO_URL = "https://zenodo.org/record/4561253/files/WELFake_Dataset.csv?download=1"

HEADERS = {"User-Agent": "AI-Security-Extension/1.0 (research project)"}


def setup_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_welfake() -> pd.DataFrame:
    print("  Downloading WELFake dataset from Zenodo…")
    # Stream the download because it's a large file (~200MB)
    response = requests.get(ZENODO_URL, headers=HEADERS, timeout=300)
    response.raise_for_status()
    df = pd.read_csv(io.BytesIO(response.content))
    print(f"    {len(df):,} rows.")
    return df


def main() -> None:
    setup_dirs()

    try:
        combined = download_welfake()
    except Exception as exc:
        raise RuntimeError(f"Download attempt failed: {exc}")

    print(f"\nTotal rows downloaded: {len(combined):,}")

    # Save the raw combined file for preprocess.py to consume
    raw_out = RAW_DIR / "welFake_raw.csv"
    combined.to_csv(raw_out, index=False)
    print(f"✓ Saved raw data → {raw_out}")
    print(f"  Columns: {list(combined.columns)}")


if __name__ == "__main__":
    main()