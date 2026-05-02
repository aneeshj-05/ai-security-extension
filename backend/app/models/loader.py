import math
import sys
from functools import lru_cache
from pathlib import Path

# ── Path patching must happen before any ml_models imports ───────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_models.phishing.features import (  # noqa: E402
    FEATURE_COLUMNS,
    features_to_vector,
)
from app.core.config import get_settings  # noqa: E402


class PhishingModel:
    def __init__(self, artifact: dict) -> None:
        self.model = artifact["model"]
        self.feature_columns = artifact.get("feature_columns", FEATURE_COLUMNS)
        self.threshold = float(
            artifact.get("threshold", get_settings().phishing_ml_threshold)
        )
        self.version = artifact.get("version", "unknown")

    def predict_probability(self, features: dict) -> float:
        vector = features_to_vector(features)
        probabilities = self.model.predict_proba([vector])[0]
        classes = list(getattr(self.model, "classes_", [0, 1]))

        if 1 in classes:
            phishing_index = classes.index(1)
        else:
            phishing_index = len(probabilities) - 1

        return float(probabilities[phishing_index])


@lru_cache
def get_phishing_model() -> "PhishingModel | None":
    model_path = Path(get_settings().phishing_model_path)

    if not model_path.exists() or model_path.stat().st_size == 0:
        return None

    try:
        import joblib

        artifact = joblib.load(model_path)
        if not isinstance(artifact, dict) or "model" not in artifact:
            return None
        return PhishingModel(artifact)
    except Exception:
        return None


class FakeNewsModel:
    def __init__(self, artifact: dict) -> None:
        self.model = artifact["model"]
        self.threshold = float(
            artifact.get("threshold", get_settings().fake_news_ml_threshold)
        )
        self.version = artifact.get("version", "unknown")

    def predict_probability(self, text: str) -> float:
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba([text])[0]
            classes = list(getattr(self.model, "classes_", [0, 1]))
            fake_index = classes.index(1) if 1 in classes else len(probabilities) - 1
            return float(probabilities[fake_index])

        if hasattr(self.model, "decision_function"):
            score = self.model.decision_function([text])
            if hasattr(score, "__len__"):
                score = score[0]
            return 1.0 / (1.0 + math.exp(-float(score)))

        prediction = self.model.predict([text])[0]
        return 1.0 if int(prediction) == 1 else 0.0


@lru_cache
def get_fake_news_model() -> "FakeNewsModel | None":
    model_path = Path(get_settings().fake_news_model_path)

    if not model_path.exists() or model_path.stat().st_size == 0:
        return None

    try:
        import joblib

        artifact = joblib.load(model_path)
        if not isinstance(artifact, dict) or "model" not in artifact:
            return None
        return FakeNewsModel(artifact)
    except Exception:
        return None
