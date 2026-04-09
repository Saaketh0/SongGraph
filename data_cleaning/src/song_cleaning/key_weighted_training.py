from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from xgboost import XGBClassifier

from song_cleaning.key_decoding import decode_argmax
from song_cleaning.key_metrics import circular_key_distance, compute_key_metrics


@dataclass
class KeyExperimentData:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


def load_key_experiment_data(
    data_path: str | pd.PathLike,
    feature_columns: list[str],
    sample_size: int,
    random_state: int,
) -> KeyExperimentData:
    columns_to_load = sorted(set(feature_columns + ["key"]))
    df = pd.read_parquet(data_path, columns=columns_to_load)

    float64_columns = df.select_dtypes(include=["float64"]).columns
    if len(float64_columns):
        df[float64_columns] = df[float64_columns].astype("float32")

    observed_df = df[df["key"].notna()].copy()

    if len(observed_df) > sample_size:
        observed_df, _ = train_test_split(
            observed_df,
            train_size=sample_size,
            random_state=random_state,
            stratify=observed_df["key"].astype("int32"),
        )

    X = observed_df[feature_columns]
    y = observed_df["key"].astype("int32")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=random_state,
        stratify=y,
    )

    return KeyExperimentData(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
    )


def build_error_weights(distances: np.ndarray) -> np.ndarray:
    weights = np.ones(len(distances), dtype=np.float32)
    weights = np.where(distances == 1, 1.25, weights)
    weights = np.where(distances == 2, 1.5, weights)
    weights = np.where(distances == 3, 1.75, weights)
    weights = np.where(distances >= 4, 2.0, weights)
    return weights.astype(np.float32)


def generate_oof_sample_weights(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_params: dict[str, object],
    n_splits: int,
    random_state: int,
) -> np.ndarray:
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    oof_predictions = np.zeros(len(y_train), dtype=np.int32)

    X_values = X_train.reset_index(drop=True)
    y_values = y_train.reset_index(drop=True)

    for train_idx, valid_idx in splitter.split(X_values, y_values):
        fold_model = XGBClassifier(**model_params)
        fold_model.fit(X_values.iloc[train_idx], y_values.iloc[train_idx])
        fold_probabilities = fold_model.predict_proba(X_values.iloc[valid_idx])
        oof_predictions[valid_idx] = decode_argmax(fold_probabilities)

    distances = circular_key_distance(y_values.to_numpy(), oof_predictions)
    return build_error_weights(distances)


def fit_and_score_key_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    model_params: dict[str, object],
    sample_weight: np.ndarray | None = None,
) -> tuple[dict[str, float], np.ndarray]:
    model = XGBClassifier(**model_params)
    model.fit(X_train, y_train, sample_weight=sample_weight)
    probabilities = model.predict_proba(X_test)
    predictions = decode_argmax(probabilities)
    metrics = compute_key_metrics(y_test.to_numpy(), predictions)
    return metrics, predictions

