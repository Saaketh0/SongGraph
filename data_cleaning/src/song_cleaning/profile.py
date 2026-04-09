import pandas as pd

from .invalid_values import collect_invalid_counts


def build_profile(df: pd.DataFrame) -> dict:
    return {
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "null_counts": {column: int(count) for column, count in df.isna().sum().items()},
        "invalid_counts": collect_invalid_counts(df),
        "duplicate_track_id_count": int(df["track_id"].dropna().duplicated().sum()),
        "unique_track_id_count": int(df["track_id"].dropna().nunique()),
    }
