from __future__ import annotations

import numpy as np


KEY_COUNT = 12


def build_circular_distance_matrix() -> np.ndarray:
    keys = np.arange(KEY_COUNT, dtype=np.int32)
    raw_distance = np.abs(keys[:, None] - keys[None, :])
    return np.minimum(raw_distance, KEY_COUNT - raw_distance).astype(np.float32)


def decode_argmax(probabilities: np.ndarray) -> np.ndarray:
    return np.asarray(np.argmax(probabilities, axis=1), dtype=np.int32)


def decode_min_expected_distance(
    probabilities: np.ndarray,
    distance_matrix: np.ndarray,
) -> np.ndarray:
    expected_distance = probabilities @ distance_matrix
    return np.asarray(np.argmin(expected_distance, axis=1), dtype=np.int32)


def max_class_confidence(probabilities: np.ndarray) -> np.ndarray:
    return np.asarray(np.max(probabilities, axis=1), dtype=np.float32)


def expected_distance_for_choice(
    probabilities: np.ndarray,
    chosen_keys: np.ndarray,
    distance_matrix: np.ndarray,
) -> np.ndarray:
    expected_distance = probabilities @ distance_matrix
    row_index = np.arange(len(chosen_keys), dtype=np.int32)
    return np.asarray(expected_distance[row_index, chosen_keys], dtype=np.float32)


def decode_top_k_min_expected_distance(
    probabilities: np.ndarray,
    distance_matrix: np.ndarray,
    top_k: int,
) -> np.ndarray:
    top_k = int(top_k)
    if top_k <= 1:
        return decode_argmax(probabilities)

    top_indices = np.argpartition(probabilities, -top_k, axis=1)[:, -top_k:]
    expected_distance = probabilities @ distance_matrix

    row_index = np.arange(probabilities.shape[0], dtype=np.int32)[:, None]
    candidate_scores = expected_distance[row_index, top_indices]
    best_local_index = np.argmin(candidate_scores, axis=1)
    return np.asarray(top_indices[np.arange(len(top_indices)), best_local_index], dtype=np.int32)


def decode_confidence_gated_top_k(
    probabilities: np.ndarray,
    distance_matrix: np.ndarray,
    confidence_threshold: float,
    top_k: int,
) -> np.ndarray:
    argmax_predictions = decode_argmax(probabilities)
    top_k_predictions = decode_top_k_min_expected_distance(
        probabilities=probabilities,
        distance_matrix=distance_matrix,
        top_k=top_k,
    )
    confidence = max_class_confidence(probabilities)
    use_top_k = confidence < float(confidence_threshold)
    return np.where(use_top_k, top_k_predictions, argmax_predictions).astype(np.int32)
