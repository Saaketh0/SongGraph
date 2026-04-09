from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import subprocess

import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


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
    "key",
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
]

THRESHOLDS = [0.5, 0.55, 0.6, 0.65, 0.7]
ZERO_CLASS_WEIGHTS = [1.0, 1.5, 2.0]
SAMPLE_SIZE = 400_000


@dataclass(frozen=True)
class ModeAnalysisResult:
    results: list[dict[str, Any]]
    missing_rows: int


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
        "n_estimators": 300,
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
        "objective": "binary:logistic",
        "eval_metric": "logloss",
    }


def load_mode_frames(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns_to_load = FEATURE_POOL + ["mode", "mode_missing"]
    df = pd.read_parquet(path, columns=columns_to_load)
    observed_df = df[df["mode_missing"] == 0].copy()
    missing_df = df[df["mode_missing"] == 1].copy()
    return observed_df, missing_df


def build_sample_weight(y: pd.Series, zero_class_weight: float) -> pd.Series:
    return y.map({0: zero_class_weight, 1: 1.0}).astype("float32")


def evaluate_threshold(
    y_true: pd.Series,
    probability_one: pd.Series,
    threshold: float,
    zero_weight: float,
    missing_probability_one: pd.Series,
) -> dict[str, Any]:
    predictions = (probability_one >= threshold).astype("int8")
    missing_predictions = (missing_probability_one >= threshold).astype("int8")
    return {
        "zero_class_weight": float(zero_weight),
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "f1_macro": float(f1_score(y_true, predictions, average="macro")),
        "precision_zero": float(precision_score(y_true, predictions, pos_label=0)),
        "recall_zero": float(recall_score(y_true, predictions, pos_label=0)),
        "predicted_zero_rate_test": float((predictions == 0).mean()),
        "predicted_zero_rate_missing": float((missing_predictions == 0).mean()) if len(missing_predictions) else 0.0,
    }


def run_mode_analysis(path: Path) -> ModeAnalysisResult:
    observed_df, missing_df = load_mode_frames(path)
    if len(observed_df) > SAMPLE_SIZE:
        observed_df = observed_df.sample(n=SAMPLE_SIZE, random_state=42)

    X = observed_df[FEATURE_POOL]
    y = observed_df["mode"].astype("int8")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    X_missing = missing_df[FEATURE_POOL]
    model_params = get_model_params(detect_xgb_device())
    results: list[dict[str, Any]] = []

    for zero_weight in ZERO_CLASS_WEIGHTS:
        sample_weight = build_sample_weight(y_train, zero_weight)
        model = XGBClassifier(**model_params)
        model.fit(X_train, y_train, sample_weight=sample_weight)

        probability_one = pd.Series(model.predict_proba(X_test)[:, 1])
        missing_probability_one = pd.Series(model.predict_proba(X_missing)[:, 1]) if len(X_missing) else pd.Series(dtype="float32")

        for threshold in THRESHOLDS:
            results.append(
                evaluate_threshold(
                    y_true=y_test,
                    probability_one=probability_one,
                    threshold=threshold,
                    zero_weight=zero_weight,
                    missing_probability_one=missing_probability_one,
                )
            )

    return ModeAnalysisResult(results=results, missing_rows=int(len(missing_df)))
