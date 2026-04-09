from __future__ import annotations

import numpy as np
import pandas as pd


KEY_COUNT = 12
MODE_MAJOR = 1.0
MODE_MINOR = -1.0


def encode_key_mode_to_xyz(
    key_values: pd.Series | np.ndarray,
    mode_values: pd.Series | np.ndarray,
) -> pd.DataFrame:
    key_array = np.asarray(key_values, dtype=np.float32)
    mode_array = np.asarray(mode_values, dtype=np.float32)

    angles = (2.0 * np.pi * key_array) / KEY_COUNT
    encoded = pd.DataFrame(
        {
            "x": np.cos(angles).astype(np.float32),
            "y": np.sin(angles).astype(np.float32),
            "z": np.where(mode_array >= 1.0, MODE_MAJOR, MODE_MINOR).astype(np.float32),
        }
    )
    return encoded


def decode_xyz_to_key_mode(
    x_values: pd.Series | np.ndarray,
    y_values: pd.Series | np.ndarray,
    z_values: pd.Series | np.ndarray,
) -> pd.DataFrame:
    x_array = np.asarray(x_values, dtype=np.float32)
    y_array = np.asarray(y_values, dtype=np.float32)
    z_array = np.asarray(z_values, dtype=np.float32)

    angles = np.arctan2(y_array, x_array)
    angles = np.mod(angles, 2.0 * np.pi)
    key_predictions = np.rint((angles * KEY_COUNT) / (2.0 * np.pi)).astype(np.int32) % KEY_COUNT
    mode_predictions = np.where(z_array >= 0.0, 1, 0).astype(np.int32)

    decoded = pd.DataFrame(
        {
            "predicted_key": key_predictions,
            "predicted_mode": mode_predictions,
        }
    )
    return decoded


def build_geometry_training_frame(
    df: pd.DataFrame,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed_mask = df["key"].notna() & df["mode"].notna()
    observed_df = df.loc[observed_mask].copy()
    features = observed_df[feature_columns].copy()
    targets = encode_key_mode_to_xyz(observed_df["key"], observed_df["mode"])
    return features, targets

