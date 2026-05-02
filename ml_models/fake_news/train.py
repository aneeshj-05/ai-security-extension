import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _THIS_DIR.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


LABEL_MAP = {
    "0": 0,
    "0.0": 0,
    "real": 0,
    "true": 0,
    "reliable": 0,
    "1": 1,
    "1.0": 1,
    "fake": 1,
    "false": 1,
    "unreliable": 1,
}


def normalize_label(value) -> int:
    key = str(value).strip().lower()

    if key in LABEL_MAP:
        return LABEL_MAP[key]

    raise ValueError(f"Unsupported label: {value!r}. Expected real/fake or 0/1.")


def combine_text(row, title_column: str, body_column: str) -> str:
    title = str(row.get(title_column, "")).strip()
    body = str(row.get(body_column, "")).strip()
    return f"{title} {body}".strip()


def train(args: argparse.Namespace) -> dict:
    data_path = Path(args.input_csv)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    for column in (args.body_column, args.label_column):
        if column not in df.columns:
            raise ValueError(f"Column {column!r} not found.")

    if args.title_column not in df.columns:
        df[args.title_column] = ""

    df = df[[args.title_column, args.body_column, args.label_column]].dropna()

    if args.max_rows:
        df = df.head(args.max_rows)

    X = df.apply(lambda row: combine_text(row, args.title_column, args.body_column), axis=1)
    y = df[args.label_column].map(normalize_label)

    class_counts = y.value_counts()
    stratify = y if len(class_counts) == 2 and class_counts.min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=stratify,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    max_df=0.8,
                    min_df=1,
                    ngram_range=(1, 2),
                    max_features=args.max_features,
                ),
            ),
            (
                "classifier",
                PassiveAggressiveClassifier(
                    max_iter=1000,
                    random_state=args.random_state,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "total_rows": len(df),
    }

    artifact = {
        "model": model,
        "threshold": args.threshold,
        "metrics": metrics,
        "version": datetime.now(timezone.utc).strftime("fake-news-pa-%Y%m%d%H%M%S"),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(data_path),
    }

    output_path = Path(args.output_model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)

    return {
        "model_path": str(output_path),
        "version": artifact["version"],
        "threshold": args.threshold,
        "metrics": metrics,
    }


_DEFAULT_DATASET = str(
    PROJECT_ROOT / "datasets" / "fake_news" / "processed" / "fake_news.csv"
)
_DEFAULT_MODEL = str(_THIS_DIR / "model.pkl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the fake-news text model.")
    parser.add_argument("input_csv", nargs="?", default=_DEFAULT_DATASET,
                        help="CSV with title/body/label columns.")
    parser.add_argument("--title-column", default="title")
    parser.add_argument("--body-column", default="body_text")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--output-model", default=_DEFAULT_MODEL)
    parser.add_argument("--threshold", type=float, default=0.75)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--max-features", type=int, default=50000)
    parser.add_argument("--max-rows", type=int, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    print(json.dumps(train(parse_args()), indent=2))
