import argparse
import json
import math
from pathlib import Path

import joblib


def predict(args: argparse.Namespace) -> dict:
    artifact = joblib.load(Path(args.model))
    model = artifact["model"]
    threshold = float(artifact.get("threshold", args.threshold))
    text = f"{args.title.strip()} {args.body_text.strip()}".strip()

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([text])[0]
        classes = list(getattr(model, "classes_", [0, 1]))
        fake_index = classes.index(1) if 1 in classes else len(probabilities) - 1
        confidence = float(probabilities[fake_index])
    elif hasattr(model, "decision_function"):
        score = model.decision_function([text])
        if hasattr(score, "__len__"):
            score = score[0]
        confidence = 1.0 / (1.0 + math.exp(-float(score)))
    else:
        prediction = int(model.predict([text])[0])
        confidence = 1.0 if prediction == 1 else 0.0

    return {
        "is_fake_news": confidence >= threshold,
        "ml_confidence": confidence,
        "threshold": threshold,
        "model_version": artifact.get("version", "unknown"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict fake-news probability.")
    parser.add_argument("--title", default="")
    parser.add_argument("--body-text", required=True)
    parser.add_argument("--model", default="ml_models/fake_news/model.pkl")
    parser.add_argument("--threshold", type=float, default=0.75)
    return parser.parse_args()


if __name__ == "__main__":
    print(json.dumps(predict(parse_args()), indent=2))
