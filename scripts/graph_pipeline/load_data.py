from __future__ import annotations

import ast
from itertools import islice
from pathlib import Path
from typing import Any

import pandas as pd


def load_song_dataset(
    input_path: str | None,
    dataset_id: str | None,
    split: str,
    load_limit: int | None,
) -> pd.DataFrame:
    if input_path:
        return _load_csv_dataset(input_path)
    if not dataset_id:
        raise ValueError("Either --input or --dataset-id must be provided.")
    return _load_huggingface_dataset(dataset_id=dataset_id, split=split, load_limit=load_limit)


def _load_csv_dataset(input_path: str) -> pd.DataFrame:
    try:
        return normalize_song_dataframe(pd.read_csv(input_path))
    except Exception as exc:
        path = Path(input_path)
        if path.exists():
            raise RuntimeError(f"Failed to load dataset from {input_path}: {exc}") from exc
        raise RuntimeError(f"CSV path does not exist: {input_path}") from exc


def _load_huggingface_dataset(
    dataset_id: str,
    split: str,
    load_limit: int | None,
) -> pd.DataFrame:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "datasets is not installed. Install it with `pip install datasets`."
        ) from exc

    cache_dir = Path.cwd() / ".cache" / "huggingface"
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        if load_limit:
            ds = load_dataset(
                dataset_id,
                split=split,
                cache_dir=str(cache_dir),
                streaming=True,
            )
            ds = ds.shuffle(seed=42, buffer_size=max(load_limit * 4, 1000))
            records = list(islice(ds, load_limit))
            frame = pd.DataFrame(records)
        else:
            ds = load_dataset(dataset_id, split=split, cache_dir=str(cache_dir))
            frame = ds.to_pandas()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load Hugging Face dataset {dataset_id!r} split {split!r}: {exc}"
        ) from exc

    return normalize_song_dataframe(frame)


def normalize_song_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()

    rename_map = {
        "name": "track_name",
        "track_genre": "genre",
    }
    applicable_renames = {
        source: target for source, target in rename_map.items() if source in normalized_df.columns
    }
    normalized_df = normalized_df.rename(columns=applicable_renames)

    if "artist" not in normalized_df.columns and "artists" in normalized_df.columns:
        normalized_df["artist"] = normalized_df["artists"].map(_extract_primary_artist)

    if "genre" not in normalized_df.columns:
        normalized_df["genre"] = None

    if "popularity" not in normalized_df.columns:
        normalized_df["popularity"] = None

    return normalized_df


def _extract_primary_artist(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, list):
        return str(value[0]).strip() if value else None
    if isinstance(value, tuple):
        return str(value[0]).strip() if value else None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = ast.literal_eval(stripped)
            except (SyntaxError, ValueError):
                parsed = None
            if isinstance(parsed, list) and parsed:
                return str(parsed[0]).strip()
        return stripped
    return str(value).strip()
