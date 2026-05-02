import argparse
import asyncio
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
for path in (PROJECT_ROOT, BACKEND_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import joblib

from app.utils.url_features import extract_features, extract_lexical_features
from ml_models.phishing.features import features_to_vector


async def predict(args: argparse.Namespace) -> dict:
    artifact = joblib.load(args.model)
    model = artifact["model"]
    threshold = float(artifact.get("threshold", args.threshold))

    if args.with_whois:
        features = await extract_features(args.url, include_whois=True)
    else:
        features = extract_lexical_features(args.url, domain_age_days=-1)

    vector = features_to_vector(features)
    probabilities = model.predict_proba([vector])[0]
    classes = list(getattr(model, "classes_", [0, 1]))
    phishing_index = classes.index(1) if 1 in classes else len(probabilities) - 1
    probability = float(probabilities[phishing_index])

    return {
        "url": args.url,
        "is_phishing": probability >= threshold,
        "ml_confidence": probability,
        "threshold": threshold,
        "model_version": artifact.get("version", "unknown"),
        "features": features,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict phishing probability for a URL.")
    parser.add_argument("url")
    parser.add_argument("--model", default="ml_models/phishing/model.pkl")
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--with-whois", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    result = asyncio.run(predict(parse_args()))
    print(json.dumps(result, indent=2))
