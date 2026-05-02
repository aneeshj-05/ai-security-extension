from argparse import Namespace

import joblib
import pandas as pd

from ml_models.phishing.features import FEATURE_COLUMNS
from ml_models.phishing.train import train


def test_tiny_fixture_trains_and_writes_artifact(tmp_path):
    dataset_path = tmp_path / "urls.csv"
    model_path = tmp_path / "model.pkl"
    pd.DataFrame(
        [
            {"url": "https://example.com", "label": 0},
            {"url": "https://openai.com", "label": 0},
            {"url": "http://secure-login-paypal.xyz/update", "label": 1},
            {"url": "http://192.168.1.1/login", "label": 1},
        ]
    ).to_csv(dataset_path, index=False)

    result = train(
        Namespace(
            input_csv=str(dataset_path),
            url_column="url",
            label_column="label",
            output_model=str(model_path),
            threshold=0.8,
            test_size=0.5,
            random_state=42,
            n_estimators=5,
            max_depth=3,
            max_rows=None,
        )
    )

    artifact = joblib.load(model_path)

    assert result["model_path"] == str(model_path)
    assert artifact["feature_columns"] == FEATURE_COLUMNS
    assert artifact["threshold"] == 0.8
    assert "metrics" in artifact
    assert "version" in artifact
