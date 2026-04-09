from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score


KEY_COUNT = 12


def circular_key_distance(
    true_keys: np.ndarray,
    predicted_keys: np.ndarray,
) -> np.ndarray:
    true_array = np.asarray(true_keys, dtype=np.int32)
    predicted_array = np.asarray(predicted_keys, dtype=np.int32)
    raw_distance = np.abs(true_array - predicted_array)
    return np.minimum(raw_distance, KEY_COUNT - raw_distance)


def compute_key_metrics(
    true_keys: np.ndarray,
    predicted_keys: np.ndarray,
) -> dict[str, float]:
    key_distance = circular_key_distance(true_keys, predicted_keys)
    return {
        "accuracy": float(accuracy_score(true_keys, predicted_keys)),
        "f1_macro": float(f1_score(true_keys, predicted_keys, average="macro")),
        "mean_key_distance": float(key_distance.mean()),
        "median_key_distance": float(np.median(key_distance)),
        "within_1_semitone": float((key_distance <= 1).mean()),
        "within_2_semitones": float((key_distance <= 2).mean()),
    }

