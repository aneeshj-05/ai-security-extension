"""
Preprocess the WELFake raw download into the format expected by train.py.

Input  : datasets/fake_news/raw/welFake_raw.csv
         Columns: Unnamed: 0, title, text, label
         label:   0 = Fake news, 1 = Real news  (WELFake convention)

Output : datasets/fake_news/processed/fake_news.csv
         Columns: title, body_text, label
         label:   1 = Fake news, 0 = Real news  (project convention)
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FILE = BASE_DIR / "datasets" / "fake_news" / "raw" / "welFake_raw.csv"
PROCESSED_FILE = BASE_DIR / "datasets" / "fake_news" / "processed" / "fake_news.csv"


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw data not found at {RAW_FILE}.\n"
            "Run `python ml_models/fake_news/fetch_dataset.py` first."
        )

    print(f"Reading {RAW_FILE} …")
    df = pd.read_csv(RAW_FILE)

    # ── Validate expected columns ──────────────────────────────────────────
    required = {"title", "text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Expected columns {required} but got {set(df.columns)}. "
            "The downloaded CSV format may have changed."
        )

    # ── Rename & retype ────────────────────────────────────────────────────
    # WELFake: 0 = Fake, 1 = Real  →  project: 1 = Fake, 0 = Real
    df = df.rename(columns={"text": "body_text"})[["title", "body_text", "label"]]
    df["label"] = df["label"].map({0: 1, 1: 0})  # invert to match LABEL_MAP

    # ── Clean ──────────────────────────────────────────────────────────────
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["body_text"] = df["body_text"].fillna("").astype(str).str.strip()
    df = df[
        (df["body_text"].str.split().str.len() >= 20) &
        (df["label"].isin([0, 1]))
    ].drop_duplicates(subset=["body_text"]).reset_index(drop=True)

    # ── Shuffle & save ─────────────────────────────────────────────────────
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)

    fake_count = (df["label"] == 1).sum()
    real_count = (df["label"] == 0).sum()
    print(f"✓ Saved {len(df):,} rows → {PROCESSED_FILE}")
    print(f"  Fake: {fake_count:,}  |  Real: {real_count:,}")


if __name__ == "__main__":
    main()
