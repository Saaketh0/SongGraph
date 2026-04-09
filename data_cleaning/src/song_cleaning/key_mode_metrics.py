from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score


KEY_COUNT = 12


def circular_key_distance(
    true_keys: pd.Series | np.ndarray,
    predicted_keys: pd.Series | np.ndarray,
) -> np.ndarray:
    true_array = np.asarray(true_keys, dtype=np.int32)
    predicted_array = np.asarray(predicted_keys, dtype=np.int32)
    raw_distance = np.abs(true_array - predicted_array)
    return np.minimum(raw_distance, KEY_COUNT - raw_distance)


def compute_key_mode_metrics(
    true_keys: pd.Series | np.ndarray,
    true_modes: pd.Series | np.ndarray,
    predicted_keys: pd.Series | np.ndarray,
    predicted_modes: pd.Series | np.ndarray,
) -> dict[str, float]:
    key_distance = circular_key_distance(true_keys, predicted_keys)
    exact_joint = (
        (np.asarray(true_keys, dtype=np.int32) == np.asarray(predicted_keys, dtype=np.int32))
        & (np.asarray(true_modes, dtype=np.int32) == np.asarray(predicted_modes, dtype=np.int32))
    )

    metrics = {
        "key_accuracy": float(accuracy_score(true_keys, predicted_keys)),
        "mode_accuracy": float(accuracy_score(true_modes, predicted_modes)),
        "joint_accuracy": float(exact_joint.mean()),
        "mean_key_distance": float(key_distance.mean()),
        "median_key_distance": float(np.median(key_distance)),
        "within_1_semitone": float((key_distance <= 1).mean()),
        "within_2_semitones": float((key_distance <= 2).mean()),
    }
    return metrics
