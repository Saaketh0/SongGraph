import pandas as pd


def apply_default_fills(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    filled = df.copy()
    explicit_fill_count = int(filled["explicit"].isna().sum())
    filled["explicit"] = filled["explicit"].fillna(0)
    return filled, {"explicit": explicit_fill_count}
