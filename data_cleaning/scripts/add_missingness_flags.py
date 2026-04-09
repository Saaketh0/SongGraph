from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "outputs" / "cleaned" / "songs_pre_imputation.parquet"
OUTPUT_PATH = ROOT / "outputs" / "cleaned" / "songs_pre_imputation_with_missingness_flags.parquet"

FEATURE_POOL = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "tempo",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "key",
    "mode",
]


def add_missingness_flags(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    flagged = df.copy()

    for column in feature_columns:
        flagged[f"{column}_missing"] = flagged[column].isna().astype("int8")

    return flagged


def main() -> None:
    df = pd.read_parquet(INPUT_PATH)
    flagged_df = add_missingness_flags(df, FEATURE_POOL)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    flagged_df.to_parquet(OUTPUT_PATH, index=False)

    added_columns = [f"{column}_missing" for column in FEATURE_POOL]
    print("input_path", INPUT_PATH)
    print("output_path", OUTPUT_PATH)
    print("added_columns", added_columns)


if __name__ == "__main__":
    main()
