from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split

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
BASE_PARAMS = {
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
SAMPLE_SIZE = 200_000
RANDOM_STATE = 42
ALPHA_GRID = [0.05, 0.1, 0.2, 0.3]
BETA_GRID = [0.5, 1.0, 2.0]


def load_data() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    columns_to_load = sorted(set(FEATURE_POOL + ["key", "mode"]))
    df = pd.read_parquet(DATA_PATH, columns=columns_to_load)

    float64_columns = df.select_dtypes(include=["float64"]).columns
    if len(float64_columns):
        df[float64_columns] = df[float64_columns].astype("float32")

    observed_df = df[df["key"].notna()].copy()
    if len(observed_df) > SAMPLE_SIZE:
        observed_df, _ = train_test_split(
            observed_df,
            train_size=SAMPLE_SIZE,
            random_state=RANDOM_STATE,
            stratify=observed_df["key"].astype("int32"),
        )

    X = observed_df[FEATURE_POOL]
    y = observed_df["key"].astype("int32")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test


def score_predictions(
    y_true: pd.Series,
    predictions,
    coordinates,
) -> dict[str, float]:
    metrics = compute_key_metrics(y_true.to_numpy(), predictions)
    metrics.update(compute_mean_2d_distance(y_true.to_numpy(), predictions, coordinates))
    return metrics


def train_baseline(
    dtrain: xgb.DMatrix,
    dtest: xgb.DMatrix,
    y_test: pd.Series,
    coordinates,
) -> dict[str, float]:
    params = dict(BASE_PARAMS)
    params["objective"] = "multi:softprob"

    model = xgb.train(params, dtrain, num_boost_round=NUM_BOOST_ROUND)
    margin = model.predict(dtest, output_margin=True)
    probabilities = softmax_from_margin(margin)
    predictions = probabilities.argmax(axis=1)
    return score_predictions(y_test, predictions, coordinates)


def train_geometric(
    dtrain: xgb.DMatrix,
    dtest: xgb.DMatrix,
    y_test: pd.Series,
    coordinates,
    distance_matrix,
    alpha: float,
    beta: float,
) -> dict[str, float]:
    soft_targets = build_soft_targets(distance_matrix=distance_matrix, alpha=alpha, beta=beta)
    objective = make_geometric_softprob_objective(soft_targets)

    model = xgb.train(dict(BASE_PARAMS), dtrain, num_boost_round=NUM_BOOST_ROUND, obj=objective)
    margin = model.predict(dtest, output_margin=True)
    probabilities = softmax_from_margin(margin)
    predictions = probabilities.argmax(axis=1)
    return score_predictions(y_test, predictions, coordinates)


def main() -> None:
    X_train, X_test, y_train, y_test = load_data()
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    coordinates = build_key_coordinates()
    distance_matrix = build_key_distance_matrix(coordinates)

    rows: list[dict[str, float | str | None]] = []

    baseline_metrics = train_baseline(dtrain=dtrain, dtest=dtest, y_test=y_test, coordinates=coordinates)
    rows.append(
        {
            "model": "baseline",
            "alpha": None,
            "beta": None,
            **baseline_metrics,
        }
    )

    for alpha in ALPHA_GRID:
        for beta in BETA_GRID:
            metrics = train_geometric(
                dtrain=dtrain,
                dtest=dtest,
                y_test=y_test,
                coordinates=coordinates,
                distance_matrix=distance_matrix,
                alpha=alpha,
                beta=beta,
            )
            rows.append(
                {
                    "model": "geometric",
                    "alpha": alpha,
                    "beta": beta,
                    **metrics,
                }
            )

    results = pd.DataFrame(rows)
    results = results.sort_values(
        ["accuracy", "f1_macro", "mean_key_distance", "mean_2d_distance"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    output_dir = ROOT / "outputs" / "profiling"
    output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_dir / "key_geometric_grid_results.csv", index=False)

    payload = {
        "data_path": str(DATA_PATH),
        "sample_size": SAMPLE_SIZE,
        "num_boost_round": NUM_BOOST_ROUND,
        "alpha_grid": ALPHA_GRID,
        "beta_grid": BETA_GRID,
        "best_row": results.iloc[0].to_dict(),
    }
    (output_dir / "key_geometric_grid_results.json").write_text(json.dumps(payload, indent=2))

    print(json.dumps(payload, indent=2))
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
