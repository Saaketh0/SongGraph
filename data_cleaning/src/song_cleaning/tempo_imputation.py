from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


TEMPO_TARGET = "tempo"

TEMPO_FEATURE_POOL = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "key",
    "mode",
    "valence_missing",
    "loudness_missing",
    "danceability_missing",
    "energy_missing",
    "acousticness_missing",
    "instrumentalness_missing",
    "liveness_missing",
    "speechiness_missing",
    "key_missing",
    "mode_missing",
]


@dataclass(frozen=True)
class TempoImputationResult:
    metrics: dict[str, float]
    missing_rows: int
    output_path: Path


def detect_xgb_device() -> str:
    build_info = xgb.build_info()
    cuda_built = str(build_info.get("USE_CUDA", "OFF")).upper() in {"ON", "TRUE", "1"}

    try:
        nvidia_smi = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        cuda_visible = nvidia_smi.returncode == 0
    except FileNotFoundError:
        cuda_visible = False

    return "cuda" if cuda_built and cuda_visible else "cpu"


def get_model_params(device: str) -> dict[str, object]:
    return {
        "objective": "reg:squarederror",
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
        "device": device,
        "random_state": 42,
        "n_jobs": -1,
    }


def load_tempo_dataset(path: Path) -> pd.DataFrame:
    columns_to_load = sorted(
        set(TEMPO_FEATURE_POOL + [TEMPO_TARGET, "tempo_missing", "track_id", "artist_name", "track_name"])
    )
    df = pd.read_parquet(path, columns=columns_to_load)
    float64_columns = df.select_dtypes(include=["float64"]).columns
    if len(float64_columns) > 0:
        df[float64_columns] = df[float64_columns].astype("float32")
    return df


def split_observed_and_missing(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed_df = df[df[TEMPO_TARGET].notna()].copy()
    missing_df = df[df[TEMPO_TARGET].isna()].copy()
    return observed_df, missing_df


def evaluate_tempo_model(
    observed_df: pd.DataFrame,
    feature_columns: list[str],
    model_params: dict[str, object],
) -> dict[str, float]:
    X = observed_df[feature_columns]
    y = observed_df[TEMPO_TARGET].astype("float32")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = XGBRegressor(**model_params)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test).astype(np.float32)

    mse = mean_squared_error(y_test, predictions)
    return {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_test, predictions)),
    }


def fit_and_impute_tempo(
    df: pd.DataFrame,
    feature_columns: list[str],
    model_params: dict[str, object],
) -> tuple[pd.DataFrame, int]:
    observed_df, missing_df = split_observed_and_missing(df)

    model = XGBRegressor(**model_params)
    model.fit(observed_df[feature_columns], observed_df[TEMPO_TARGET].astype("float32"))

    predictions = model.predict(missing_df[feature_columns]).astype(np.float32)
    predictions = np.maximum(predictions, np.float32(0.0))

    result_df = df.copy()
    missing_idx = missing_df.index
    result_df.loc[missing_idx, TEMPO_TARGET] = predictions

    return result_df, int(len(missing_idx))


def impute_tempo_file(input_path: Path, output_path: Path) -> TempoImputationResult:
    device = detect_xgb_device()
    model_params = get_model_params(device)
    feature_columns = list(TEMPO_FEATURE_POOL)

    df = load_tempo_dataset(input_path)
    observed_df, _ = split_observed_and_missing(df)
    metrics = evaluate_tempo_model(observed_df, feature_columns, model_params)
    result_df, missing_rows = fit_and_impute_tempo(df, feature_columns, model_params)
    result_df.to_parquet(output_path)

    return TempoImputationResult(
        metrics=metrics,
        missing_rows=missing_rows,
        output_path=output_path,
    )
