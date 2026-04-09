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
ALPHA_GRID = [0.4, 0.5]
BETA_GRID = [1.0, 2.0, 3.0]
ORDERINGS = ["chromatic", "fifths"]
KERNELS = ["gaussian_squared", "gaussian_linear"]


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
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

    return train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def score_predictions(
    y_true: pd.Series,
    predictions,
    coordinates,
) -> dict[str, float]:
    metrics = compute_key_metrics(y_true.to_numpy(), predictions)
    metrics.update(compute_mean_2d_distance(y_true.to_numpy(), predictions, coordinates))
    return metrics


def main() -> None:
    X_train, X_test, y_train, y_test = load_data()
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    rows: list[dict[str, float | str | None]] = []

    baseline_coordinates = build_key_coordinates(ordering="chromatic")
    baseline_params = dict(BASE_PARAMS)
    baseline_params["objective"] = "multi:softprob"
    baseline_model = xgb.train(baseline_params, dtrain, num_boost_round=NUM_BOOST_ROUND)
    baseline_margin = baseline_model.predict(dtest, output_margin=True)
    baseline_probabilities = softmax_from_margin(baseline_margin)
    baseline_predictions = baseline_probabilities.argmax(axis=1)
    baseline_metrics = score_predictions(y_test, baseline_predictions, baseline_coordinates)
    rows.append(
        {
            "model": "baseline",
            "ordering": "chromatic",
            "kernel": None,
            "alpha": None,
            "beta": None,
            **baseline_metrics,
        }
    )

    for ordering in ORDERINGS:
        coordinates = build_key_coordinates(ordering=ordering)
        distance_matrix = build_key_distance_matrix(coordinates=coordinates)
        for kernel in KERNELS:
            for alpha in ALPHA_GRID:
                for beta in BETA_GRID:
                    soft_targets = build_soft_targets(
                        distance_matrix=distance_matrix,
                        alpha=alpha,
                        beta=beta,
                        kernel=kernel,
                    )
                    objective = make_geometric_softprob_objective(soft_targets)
                    model = xgb.train(dict(BASE_PARAMS), dtrain, num_boost_round=NUM_BOOST_ROUND, obj=objective)
                    margin = model.predict(dtest, output_margin=True)
                    probabilities = softmax_from_margin(margin)
                    predictions = probabilities.argmax(axis=1)
                    metrics = score_predictions(y_test, predictions, coordinates)
                    row = {
                        "model": "geometric",
                        "ordering": ordering,
                        "kernel": kernel,
                        "alpha": alpha,
                        "beta": beta,
                        **metrics,
                    }
                    rows.append(row)
                    print(
                        "done",
                        ordering,
                        kernel,
                        alpha,
                        beta,
                        row["accuracy"],
                        row["f1_macro"],
                        flush=True,
                    )

    results = pd.DataFrame(rows).sort_values(
        ["accuracy", "f1_macro", "mean_key_distance", "mean_2d_distance"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    output_dir = ROOT / "outputs" / "profiling"
    output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_dir / "key_geometric_variant_results.csv", index=False)

    payload = {
        "data_path": str(DATA_PATH),
        "sample_size": SAMPLE_SIZE,
        "num_boost_round": NUM_BOOST_ROUND,
        "orderings": ORDERINGS,
        "kernels": KERNELS,
        "alpha_grid": ALPHA_GRID,
        "beta_grid": BETA_GRID,
        "best_row": results.iloc[0].to_dict(),
    }
    (output_dir / "key_geometric_variant_results.json").write_text(json.dumps(payload, indent=2))

    print(json.dumps(payload, indent=2))
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
