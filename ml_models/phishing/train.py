import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _THIS_DIR.parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
for _p in (PROJECT_ROOT, BACKEND_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.utils.url_features import extract_lexical_features
from ml_models.phishing.features import FEATURE_COLUMNS, features_to_vector


LABEL_MAP = {
    "0": 0,
    "0.0": 0,
    "safe": 0,
    "benign": 0,
    "legitimate": 0,
    "legit": 0,
    "1": 1,
    "1.0": 1,
    "phish": 1,
    "phishing": 1,
}


def normalize_label(value) -> int:
    key = str(value).strip().lower()

    if key in LABEL_MAP:
        return LABEL_MAP[key]

    raise ValueError(f"Unsupported label: {value!r}. Expected 0/1 or benign/phishing.")


def build_feature_matrix(urls: pd.Series) -> list[list[float]]:
    matrix = []

    for url in urls:
        features = extract_lexical_features(str(url), domain_age_days=-1)
        matrix.append(features_to_vector(features))

    return matrix


def train(args: argparse.Namespace) -> dict:
    data_path = Path(args.input_csv)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    if args.url_column not in df.columns:
        raise ValueError(f"URL column {args.url_column!r} not found.")

    if args.label_column not in df.columns:
        raise ValueError(f"Label column {args.label_column!r} not found.")

    df = df[[args.url_column, args.label_column]].dropna().drop_duplicates()

    if args.max_rows:
        df = df.head(args.max_rows)

    y = df[args.label_column].map(normalize_label)
    X = build_feature_matrix(df[args.url_column])

    class_counts = y.value_counts()
    stratify = y if len(class_counts) == 2 and class_counts.min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        class_weight="balanced",
        random_state=args.random_state,
        n_jobs=-1,
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
        "feature_columns": FEATURE_COLUMNS,
        "threshold": args.threshold,
        "metrics": metrics,
        "version": datetime.now(timezone.utc).strftime("phishing-rf-%Y%m%d%H%M%S"),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(data_path),
    }

    output_path = Path(args.output_model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)

    return {
        "model_path": str(output_path),
        "version": artifact["version"],
        "feature_columns": FEATURE_COLUMNS,
        "threshold": args.threshold,
        "metrics": metrics,
    }


_DEFAULT_DATASET = str(
    PROJECT_ROOT / "datasets" / "phishing" / "processed" / "phishing_urls.csv"
)
_DEFAULT_MODEL = str(_THIS_DIR / "model.pkl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the phishing URL model.")
    parser.add_argument("input_csv", nargs="?", default=_DEFAULT_DATASET,
                        help="CSV with URL and label columns.")
    parser.add_argument("--url-column", default="url")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--output-model", default=_DEFAULT_MODEL)
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--max-rows", type=int, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    result = train(parse_args())
    print(json.dumps(result, indent=2))
