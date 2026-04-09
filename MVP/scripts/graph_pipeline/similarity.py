from __future__ import annotations

import numpy as np
import pandas as pd


SIMILARITY_FEATURE_COLUMNS = [
    "danceability",
    "energy",
    "tempo",
    "valence",
    "acousticness",
    "speechiness",
    "instrumentalness",
    "liveness",
    "popularity",
]


def build_similarity_edges(df: pd.DataFrame, k: int) -> list[dict]:
    if len(df) < 2 or k <= 0:
        return []

    feature_columns = [column for column in SIMILARITY_FEATURE_COLUMNS if column in df.columns]
    if not feature_columns:
        return []

    feature_frame = df[feature_columns].apply(pd.to_numeric, errors="coerce")
    feature_frame = feature_frame.fillna(feature_frame.median(numeric_only=True)).fillna(0.0)
    normalized_matrix = _z_score_normalize(feature_frame.to_numpy(dtype=float))
    similarity_matrix = _cosine_similarity_matrix(normalized_matrix)

    song_ids = df["song_id"].tolist()
    edge_keys: set[tuple[str, str]] = set()
    edges: list[dict] = []
    neighbor_count = min(k, len(song_ids) - 1)

    for index, source_id in enumerate(song_ids):
        neighbor_indices = _top_neighbor_indices(similarity_matrix[index], index, neighbor_count)
        for neighbor_index in neighbor_indices:
            target_id = song_ids[neighbor_index]
            edge_key = (source_id, target_id)
            if edge_key in edge_keys:
                continue
            edge_keys.add(edge_key)
            edges.append(
                {
                    "source": source_id,
                    "target": target_id,
                    "type": "SIMILAR_TO",
                    "score": round(
                        _normalize_similarity_score(similarity_matrix[index, neighbor_index]),
                        4,
                    ),
                }
            )
    return edges


def _z_score_normalize(matrix: np.ndarray) -> np.ndarray:
    means = matrix.mean(axis=0, keepdims=True)
    stds = matrix.std(axis=0, keepdims=True)
    stds[stds == 0] = 1.0
    return (matrix - means) / stds


def _cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = matrix / norms
    return normalized @ normalized.T


def _top_neighbor_indices(row: np.ndarray, self_index: int, neighbor_count: int) -> list[int]:
    ranked_indices = np.argsort(row)[::-1]
    neighbors: list[int] = []
    for candidate in ranked_indices:
        if candidate == self_index:
            continue
        neighbors.append(int(candidate))
        if len(neighbors) == neighbor_count:
            break
    return neighbors


def _normalize_similarity_score(raw_score: float) -> float:
    return (float(raw_score) + 1.0) / 2.0
