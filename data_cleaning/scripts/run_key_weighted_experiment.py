from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

import numpy as np
import pandas as pd

from song_cleaning.key_weighted_training import (
    fit_and_score_key_model,
    generate_oof_sample_weights,
    load_key_experiment_data,
)


DATA_PATH = ROOT / "liveness_final.parquet"
FEATURE_COLUMNS = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "tempo",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "mode",
    "valence_missing",
    "loudness_missing",
    "danceability_missing",
    "energy_missing",
    "tempo_missing",
    "acousticness_missing",
    "instrumentalness_missing",
    "liveness_missing",
    "speechiness_missing",
    "key_missing",
    "mode_missing",
]
MODEL_PARAMS = {
    "objective": "multi:softprob",
    "num_class": 12,
    "eval_metric": "mlogloss",
    "n_estimators": 600,
    "max_depth": 6,
    "learning_rate": 0.03,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 1.0,
    "reg_alpha": 0.0,
    "reg_lambda": 1.0,
    "gamma": 0.0,
    "tree_method": "hist",
    "random_state": 42,
    "n_jobs": -1,
}
SAMPLE_SIZE = 200_000
RANDOM_STATE = 42
OOF_SPLITS = 5


def main() -> None:
    experiment_data = load_key_experiment_data(
        data_path=DATA_PATH,
        feature_columns=FEATURE_COLUMNS,
        sample_size=SAMPLE_SIZE,
        random_state=RANDOM_STATE,
    )

    baseline_metrics, _ = fit_and_score_key_model(
        X_train=experiment_data.X_train,
        X_test=experiment_data.X_test,
        y_train=experiment_data.y_train,
        y_test=experiment_data.y_test,
        model_params=MODEL_PARAMS,
    )

    sample_weights = generate_oof_sample_weights(
        X_train=experiment_data.X_train,
        y_train=experiment_data.y_train,
        model_params=MODEL_PARAMS,
        n_splits=OOF_SPLITS,
        random_state=RANDOM_STATE,
    )

    weighted_metrics, _ = fit_and_score_key_model(
        X_train=experiment_data.X_train,
        X_test=experiment_data.X_test,
        y_train=experiment_data.y_train,
        y_test=experiment_data.y_test,
        model_params=MODEL_PARAMS,
        sample_weight=sample_weights,
    )

    weight_summary = {
        "min": float(sample_weights.min()),
        "max": float(sample_weights.max()),
        "mean": float(sample_weights.mean()),
        "std": float(sample_weights.std()),
        "p50": float(np.quantile(sample_weights, 0.5)),
        "p90": float(np.quantile(sample_weights, 0.9)),
        "p99": float(np.quantile(sample_weights, 0.99)),
    }

    comparison = pd.DataFrame(
        [
            {"model": "baseline_argmax", **baseline_metrics},
            {"model": "weighted_argmax", **weighted_metrics},
        ]
    )

    result = {
        "data_path": str(DATA_PATH),
        "sample_size": SAMPLE_SIZE,
        "oof_splits": OOF_SPLITS,
        "weight_summary": weight_summary,
        "baseline_metrics": baseline_metrics,
        "weighted_metrics": weighted_metrics,
    }

    output_dir = ROOT / "outputs" / "profiling"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "key_weighted_experiment.json").write_text(json.dumps(result, indent=2))
    comparison.to_csv(output_dir / "key_weighted_experiment.csv", index=False)

    print(json.dumps(result, indent=2))
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
