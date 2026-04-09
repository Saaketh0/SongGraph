from __future__ import annotations

import numpy as np


KEY_COUNT = 12


def build_key_coordinates(ordering: str = "chromatic") -> np.ndarray:
    coordinates = np.zeros((KEY_COUNT, 2), dtype=np.float32)
    for key in range(KEY_COUNT):
        if ordering == "chromatic":
            position = key
        elif ordering == "fifths":
            position = (7 * key) % KEY_COUNT
        else:
            raise ValueError(f"Unsupported key ordering: {ordering}")

        angle = (2.0 * np.pi * position) / KEY_COUNT
        coordinates[key, 0] = np.cos(angle)
        coordinates[key, 1] = np.sin(angle)
    return coordinates


def build_key_distance_matrix(
    coordinates: np.ndarray | None = None,
    ordering: str = "chromatic",
) -> np.ndarray:
    if coordinates is None:
        coordinates = build_key_coordinates(ordering=ordering)
    deltas = coordinates[:, None, :] - coordinates[None, :, :]
    return np.linalg.norm(deltas, axis=2).astype(np.float32)


def build_soft_targets(
    distance_matrix: np.ndarray,
    alpha: float,
    beta: float,
    kernel: str = "gaussian_squared",
) -> np.ndarray:
    distance_array = np.asarray(distance_matrix, dtype=np.float32)

    if kernel == "gaussian_squared":
        soft_weights = np.exp(-float(beta) * np.square(distance_array))
    elif kernel == "gaussian_linear":
        soft_weights = np.exp(-float(beta) * distance_array)
    else:
        raise ValueError(f"Unsupported kernel: {kernel}")

    soft_weights /= soft_weights.sum(axis=1, keepdims=True)

    one_hot = np.eye(distance_array.shape[0], dtype=np.float32)
    mixed = (1.0 - float(alpha)) * one_hot + float(alpha) * soft_weights
    mixed /= mixed.sum(axis=1, keepdims=True)
    return mixed.astype(np.float32)


def softmax_from_margin(margin: np.ndarray, num_class: int = KEY_COUNT) -> np.ndarray:
    margin = np.asarray(margin, dtype=np.float32)
    if margin.ndim == 1:
        margin = margin.reshape(-1, num_class)
    shifted = margin - margin.max(axis=1, keepdims=True)
    exp_margin = np.exp(shifted)
    return (exp_margin / exp_margin.sum(axis=1, keepdims=True)).astype(np.float32)


def make_geometric_softprob_objective(soft_targets: np.ndarray):
    soft_targets = np.asarray(soft_targets, dtype=np.float32)
    num_class = soft_targets.shape[0]

    def objective(predt: np.ndarray, dtrain) -> tuple[np.ndarray, np.ndarray]:
        predictions = np.asarray(predt, dtype=np.float32)
        if predictions.ndim == 1:
            predictions = predictions.reshape(-1, num_class)

        labels = dtrain.get_label().astype(np.int32)
        targets = soft_targets[labels]
        probabilities = softmax_from_margin(predictions, num_class=num_class)

        grad = probabilities - targets
        hess = np.maximum(probabilities * (1.0 - probabilities), 1e-6)
        return grad.reshape(-1), hess.reshape(-1)

    return objective


def compute_mean_2d_distance(
    true_keys: np.ndarray,
    predicted_keys: np.ndarray,
    coordinates: np.ndarray | None = None,
) -> dict[str, float]:
    if coordinates is None:
        coordinates = build_key_coordinates()
    true_xyz = coordinates[np.asarray(true_keys, dtype=np.int32)]
    predicted_xyz = coordinates[np.asarray(predicted_keys, dtype=np.int32)]
    distance = np.linalg.norm(true_xyz - predicted_xyz, axis=1)
    return {
        "mean_2d_distance": float(distance.mean()),
        "median_2d_distance": float(np.median(distance)),
    }
