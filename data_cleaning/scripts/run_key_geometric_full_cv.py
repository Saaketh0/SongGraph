from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from song_cleaning.key_geometric_loss import (
    build_key_coordinates,
    build_key_distance_matrix,
    build_soft_targets,
    compute_mean_2d_distance,
    make_geometric_softprob_objective,
    softmax_from_margin,
)
from song_cleaning.key_metrics import compute_key_metrics


DATA_PATH = ROOT / "liveness_final.parquet"
FEATURE_POOL = [
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
    "num_class": 12,
    "max_depth": 6,
    "eta": 0.03,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 1.0,
    "alpha": 0.0,
    "lambda": 1.0,
    "gamma": 0.0,
    "tree_method": "hist",
    "seed": 42,
    "disable_default_eval_metric": 1,
}
NUM_BOOST_ROUND = 200
N_SPLITS = 5
ALPHA = 0.4
BETA = 2.0
ORDERING = "chromatic"
KERNEL = "gaussian_squared"
RANDOM_STATE = 42


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    columns_to_load = sorted(set(FEATURE_POOL + ["key"]))
    df = pd.read_parquet(DATA_PATH, columns=columns_to_load)

    float64_columns = df.select_dtypes(include=["float64"]).columns
    if len(float64_columns):
        df[float64_columns] = df[float64_columns].astype("float32")

    observed_df = df[df["key"].notna()].copy()
    X = observed_df[FEATURE_POOL]
    y = observed_df["key"].astype("int32")
    return X, y


def summarize_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    frame = pd.DataFrame(rows)
    summary: dict[str, float] = {}
    for column in frame.columns:
        summary[f"{column}_mean"] = float(frame[column].mean())
        summary[f"{column}_std"] = float(frame[column].std(ddof=0))
    return summary


def main() -> None:
    X, y = load_data()
    coordinates = build_key_coordinates(ordering=ORDERING)
    distance_matrix = build_key_distance_matrix(coordinates=coordinates)
    soft_targets = build_soft_targets(
        distance_matrix=distance_matrix,
        alpha=ALPHA,
        beta=BETA,
        kernel=KERNEL,
    )
    objective = make_geometric_softprob_objective(soft_targets)

    splitter = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    fold_rows: list[dict[str, float]] = []

    for fold_index, (train_idx, test_idx) in enumerate(splitter.split(X, y), start=1):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)

        model = xgb.train(dict(MODEL_PARAMS), dtrain, num_boost_round=NUM_BOOST_ROUND, obj=objective)
        margin = model.predict(dtest, output_margin=True)
        probabilities = softmax_from_margin(margin)
        predictions = probabilities.argmax(axis=1)

        metrics = compute_key_metrics(y_test.to_numpy(), predictions)
        metrics.update(compute_mean_2d_distance(y_test.to_numpy(), predictions, coordinates))
        metrics["fold"] = float(fold_index)
        fold_rows.append(metrics)
        print(json.dumps({"fold": fold_index, **metrics}))

    fold_frame = pd.DataFrame(fold_rows)
    summary = summarize_metrics(
        [
            {key: value for key, value in row.items() if key != "fold"}
            for row in fold_rows
        ]
    )

    payload = {
        "data_path": str(DATA_PATH),
        "n_splits": N_SPLITS,
        "num_boost_round": NUM_BOOST_ROUND,
        "alpha": ALPHA,
        "beta": BETA,
        "ordering": ORDERING,
        "kernel": KERNEL,
        "summary": summary,
    }

    output_dir = ROOT / "outputs" / "profiling"
    output_dir.mkdir(parents=True, exist_ok=True)
    fold_frame.to_csv(output_dir / "key_geometric_full_cv_folds.csv", index=False)
    (output_dir / "key_geometric_full_cv_summary.json").write_text(json.dumps(payload, indent=2))

    print(json.dumps(payload, indent=2))
    print(fold_frame.to_string(index=False))


if __name__ == "__main__":
    main()
