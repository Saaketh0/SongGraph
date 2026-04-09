from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from song_cleaning.key_geometric_loss import (
    build_key_coordinates,
    build_key_distance_matrix,
    build_soft_targets,
    make_geometric_softprob_objective,
    softmax_from_margin,
)


INPUT_PATH = ROOT / "liveness_final.parquet"
OUTPUT_PATH = ROOT / "finalv1.parquet"
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
GEOMETRIC_ALPHA = 0.4
GEOMETRIC_BETA = 2.0
GEOMETRIC_ORDERING = "chromatic"
GEOMETRIC_KERNEL = "gaussian_squared"


def main() -> None:
    df = pd.read_parquet(INPUT_PATH)

    float64_columns = df.select_dtypes(include=["float64"]).columns
    if len(float64_columns):
        df[float64_columns] = df[float64_columns].astype("float32")

    observed_mask = df["key"].notna()
    missing_mask = df["key"].isna()

    X_observed = df.loc[observed_mask, FEATURE_POOL]
    y_observed = df.loc[observed_mask, "key"].astype("int32")
    X_missing = df.loc[missing_mask, FEATURE_POOL]

    dtrain = xgb.DMatrix(X_observed, label=y_observed)

    coordinates = build_key_coordinates(ordering=GEOMETRIC_ORDERING)
    distance_matrix = build_key_distance_matrix(coordinates=coordinates)
    soft_targets = build_soft_targets(
        distance_matrix=distance_matrix,
        alpha=GEOMETRIC_ALPHA,
        beta=GEOMETRIC_BETA,
        kernel=GEOMETRIC_KERNEL,
    )
    objective = make_geometric_softprob_objective(soft_targets)

    model = xgb.train(dict(MODEL_PARAMS), dtrain, num_boost_round=NUM_BOOST_ROUND, obj=objective)

    if int(missing_mask.sum()) > 0:
        dmissing = xgb.DMatrix(X_missing)
        missing_margin = model.predict(dmissing, output_margin=True)
        missing_probabilities = softmax_from_margin(missing_margin)
        missing_predictions = missing_probabilities.argmax(axis=1).astype("int32")
        df.loc[missing_mask, "key"] = missing_predictions

    if "key" in df.columns:
        df["key"] = df["key"].astype("Int32")

    df.to_parquet(OUTPUT_PATH)

    payload = {
        "input_path": str(INPUT_PATH),
        "output_path": str(OUTPUT_PATH),
        "observed_key_rows": int(observed_mask.sum()),
        "imputed_key_rows": int(missing_mask.sum()),
        "num_boost_round": NUM_BOOST_ROUND,
        "alpha": GEOMETRIC_ALPHA,
        "beta": GEOMETRIC_BETA,
        "ordering": GEOMETRIC_ORDERING,
        "kernel": GEOMETRIC_KERNEL,
    }

    output_dir = ROOT / "outputs" / "profiling"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "finalv1_key_imputation.json").write_text(json.dumps(payload, indent=2))

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
