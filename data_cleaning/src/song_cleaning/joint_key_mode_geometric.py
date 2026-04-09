from __future__ import annotations

import numpy as np
import pandas as pd


KEY_COUNT = 12
MODE_COUNT = 2
JOINT_CLASS_COUNT = KEY_COUNT * MODE_COUNT


def encode_joint_class(
    key_values: pd.Series | np.ndarray,
    mode_values: pd.Series | np.ndarray,
) -> np.ndarray:
    key_array = np.asarray(key_values, dtype=np.int32)
    mode_array = np.asarray(mode_values, dtype=np.int32)
    return (mode_array * KEY_COUNT + key_array).astype(np.int32)


def decode_joint_class(class_ids: pd.Series | np.ndarray) -> pd.DataFrame:
    class_array = np.asarray(class_ids, dtype=np.int32)
    decoded = pd.DataFrame(
        {
            "predicted_key": (class_array % KEY_COUNT).astype(np.int32),
            "predicted_mode": (class_array // KEY_COUNT).astype(np.int32),
        }
    )
    return decoded


def build_joint_coordinates() -> np.ndarray:
    coordinates = np.zeros((JOINT_CLASS_COUNT, 3), dtype=np.float32)
    for mode in range(MODE_COUNT):
        z_value = 1.0 if mode == 1 else -1.0
        for key in range(KEY_COUNT):
            class_id = mode * KEY_COUNT + key
            angle = (2.0 * np.pi * key) / KEY_COUNT
            coordinates[class_id, 0] = np.cos(angle)
            coordinates[class_id, 1] = np.sin(angle)
            coordinates[class_id, 2] = z_value
    return coordinates


def build_joint_distance_matrix(coordinates: np.ndarray | None = None) -> np.ndarray:
    if coordinates is None:
        coordinates = build_joint_coordinates()
    deltas = coordinates[:, None, :] - coordinates[None, :, :]
    return np.linalg.norm(deltas, axis=2).astype(np.float32)


def build_soft_targets(
    distance_matrix: np.ndarray,
    alpha: float,
    beta: float,
) -> np.ndarray:
    distance_array = np.asarray(distance_matrix, dtype=np.float32)
    soft_weights = np.exp(-float(beta) * np.square(distance_array))
    soft_weights /= soft_weights.sum(axis=1, keepdims=True)

    one_hot = np.eye(distance_array.shape[0], dtype=np.float32)
    mixed = (1.0 - float(alpha)) * one_hot + float(alpha) * soft_weights
    mixed /= mixed.sum(axis=1, keepdims=True)
    return mixed.astype(np.float32)


def softmax_from_margin(margin: np.ndarray) -> np.ndarray:
    margin = np.asarray(margin, dtype=np.float32)
    if margin.ndim == 1:
        margin = margin.reshape(-1, JOINT_CLASS_COUNT)
    shifted = margin - margin.max(axis=1, keepdims=True)
    exp_margin = np.exp(shifted)
    return (exp_margin / exp_margin.sum(axis=1, keepdims=True)).astype(np.float32)


def make_geometric_softprob_objective(
    soft_targets: np.ndarray,
):
    soft_targets = np.asarray(soft_targets, dtype=np.float32)
    num_class = soft_targets.shape[0]

    def objective(predt: np.ndarray, dtrain) -> tuple[np.ndarray, np.ndarray]:
        predictions = np.asarray(predt, dtype=np.float32)
        if predictions.ndim == 1:
            predictions = predictions.reshape(-1, num_class)

        labels = dtrain.get_label().astype(np.int32)
        targets = soft_targets[labels]
        probabilities = softmax_from_margin(predictions)

        grad = probabilities - targets
        hess = np.maximum(probabilities * (1.0 - probabilities), 1e-6)
        return grad.reshape(-1), hess.reshape(-1)

    return objective


def compute_joint_metrics(
    true_keys: pd.Series | np.ndarray,
    true_modes: pd.Series | np.ndarray,
    predicted_keys: pd.Series | np.ndarray,
    predicted_modes: pd.Series | np.ndarray,
    coordinates: np.ndarray | None = None,
) -> dict[str, float]:
    if coordinates is None:
        coordinates = build_joint_coordinates()

    true_joint = encode_joint_class(true_keys, true_modes)
    predicted_joint = encode_joint_class(predicted_keys, predicted_modes)

    true_key_array = np.asarray(true_keys, dtype=np.int32)
    predicted_key_array = np.asarray(predicted_keys, dtype=np.int32)
    true_mode_array = np.asarray(true_modes, dtype=np.int32)
    predicted_mode_array = np.asarray(predicted_modes, dtype=np.int32)

    key_distance = np.abs(true_key_array - predicted_key_array)
    key_distance = np.minimum(key_distance, KEY_COUNT - key_distance)

    true_xyz = coordinates[true_joint]
    predicted_xyz = coordinates[predicted_joint]
    geometric_distance = np.linalg.norm(true_xyz - predicted_xyz, axis=1)

    return {
        "joint_accuracy": float((true_joint == predicted_joint).mean()),
        "key_accuracy": float((true_key_array == predicted_key_array).mean()),
        "mode_accuracy": float((true_mode_array == predicted_mode_array).mean()),
        "mean_key_distance": float(key_distance.mean()),
        "median_key_distance": float(np.median(key_distance)),
        "within_1_semitone": float((key_distance <= 1).mean()),
        "within_2_semitones": float((key_distance <= 2).mean()),
        "mean_3d_distance": float(geometric_distance.mean()),
        "median_3d_distance": float(np.median(geometric_distance)),
    }
