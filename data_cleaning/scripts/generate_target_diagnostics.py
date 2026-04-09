from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "diagnostics"
DATA_PATH = 'ROOT / "outputs" / "cleaned" / "songs_pre_imputation_with_missingness_flags.parquet"'

REGRESSION_TARGETS = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
]

CLASSIFICATION_TARGETS = [
    "key",
    "mode",
]

TARGET_COLUMNS = REGRESSION_TARGETS + CLASSIFICATION_TARGETS

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
    "valence_missing",
    "loudness_missing",
    "danceability_missing",
    "energy_missing",
    "tempo_missing",
    "acousticness_missing",
    "instrumentalness_missing",
    "liveness_missing",
    "speechiness_missing",
    "key_missing",
    "mode_missing",
]

BEST_PARAMS = {
    "n_estimators": 300,
    "max_depth": 10,
    "learning_rate": 0.08960785365368121,
    "subsample": 0.8394633936788146,
    "colsample_bytree": 0.6624074561769746,
    "min_child_weight": 2.403950683025824,
    "reg_alpha": 3.3323645788192616e-08,
    "reg_lambda": 0.6245760287469887,
    "gamma": 0.002570603566117596,
    "objective": "reg:squarederror",
    "tree_method": "hist",
    "random_state": 42,
    "n_jobs": -1,
}


def code_cell(lines: list[str]) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line if line.endswith("\n") else f"{line}\n" for line in lines],
    }


def build_notebook(target: str) -> dict:
    target_type = "regression" if target in REGRESSION_TARGETS else "classification"
    common_setup = code_cell(
        [
            "from pathlib import Path",
            "",
            "import numpy as np",
            "import pandas as pd",
            "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score",
            "from sklearn.model_selection import train_test_split",
            "from xgboost import XGBRegressor",
            "",
            "ROOT = Path.cwd()",
            f'DATA_PATH = {DATA_PATH}',
            f'TARGET = "{target}"',
            f'TARGET_TYPE = "{target_type}"',
            "",
            f"TARGET_COLUMNS = {repr(TARGET_COLUMNS)}",
            f"REGRESSION_TARGETS = {repr(REGRESSION_TARGETS)}",
            f"FEATURE_POOL = {repr(FEATURE_POOL)}",
            "",
            "feature_columns = [column for column in FEATURE_POOL if column != TARGET]",
            f"best_params = {repr(BEST_PARAMS)}",
        ]
    )

    load_cell = code_cell(
        [
            'columns_to_load = sorted(set(FEATURE_POOL + ["track_id", "artist_name", "track_name"]))',
            "df = pd.read_parquet(DATA_PATH, columns=columns_to_load)",
            "df.shape",
        ]
    )

    basic_target_cell = code_cell(
        [
            "rows = len(df)",
            "missing_count = int(df[TARGET].isna().sum())",
            "observed_count = int(df[TARGET].notna().sum())",
            "missing_pct = missing_count / rows",
            'print({"target": TARGET, "type": TARGET_TYPE, "rows": rows, "missing_count": missing_count, "missing_pct": missing_pct, "observed_count": observed_count})',
        ]
    )

    summary_cell_lines = [
        "if TARGET_TYPE == 'regression':",
        "    display(df[TARGET].describe())",
        "else:",
        "    display(df[TARGET].value_counts(dropna=False).sort_index())",
    ]
    summary_cell = code_cell(summary_cell_lines)

    split_cell = code_cell(
        [
            "observed_df = df[df[TARGET].notna()].copy()",
            "missing_df = df[df[TARGET].isna()].copy()",
            "X_missing = missing_df[feature_columns]",
            "",
            'print({"observed_rows": len(observed_df), "missing_rows": len(missing_df), "feature_count": len(feature_columns)})',
        ]
    )

    missing_feature_cell = code_cell(
        [
            "missing_feature_summary = pd.DataFrame({",
            '    "missing_rows_non_null_count": X_missing.notna().sum(),',
            '    "missing_rows_null_count": X_missing.isna().sum(),',
            '    "missing_rows_nunique": X_missing.nunique(),',
            "}).sort_values(['missing_rows_null_count', 'missing_rows_nunique'], ascending=[False, True])",
            "missing_feature_summary",
        ]
    )

    row_coverage_cell = code_cell(
        [
            "row_non_null_counts = X_missing.notna().sum(axis=1)",
            "row_non_null_counts.describe()",
        ]
    )

    missing_rows_cell = code_cell(
        [
            "missing_df.isna().sum().sort_values(ascending=False)",
        ]
    )

    sample_rows_cell = code_cell(
        [
            'missing_df[["track_id", "artist_name", "track_name", TARGET]].head(20)',
        ]
    )

    correlation_cell = code_cell(
        [
            "if TARGET in REGRESSION_TARGETS:",
            "    display(df[REGRESSION_TARGETS].corr(numeric_only=True)[TARGET].drop(TARGET).sort_values(key=lambda s: s.abs(), ascending=False))",
            "else:",
            "    print('Classification target; skipping numeric correlation ranking.')",
        ]
    )

    fit_cell = code_cell(
        [
            "if TARGET_TYPE == 'regression' and missing_count > 0:",
            "    X_observed = observed_df[feature_columns]",
            "    y_observed = observed_df[TARGET]",
            "    X_train, X_test, y_train, y_test = train_test_split(",
            "        X_observed,",
            "        y_observed,",
            "        test_size=0.2,",
            "        random_state=42,",
            "    )",
            "    model = XGBRegressor(**best_params)",
            "    model.fit(X_train, y_train)",
            "    test_predictions = np.clip(model.predict(X_test), 0, 1)",
            "    display({",
            '        "mae": mean_absolute_error(y_test, test_predictions),',
            '        "rmse": np.sqrt(mean_squared_error(y_test, test_predictions)),',
            '        "r2": r2_score(y_test, test_predictions),',
            "    })",
            "    final_model = XGBRegressor(**best_params)",
            "    final_model.fit(X_observed, y_observed)",
            "    predictions = np.clip(final_model.predict(X_missing), 0, 1)",
            "    display(pd.Series(test_predictions).describe())",
            "    display(pd.Series(test_predictions).nunique())",
            "    display(pd.Series(predictions).describe())",
            "    display(pd.Series(predictions).nunique())",
            "else:",
            "    print('Skipping regressor fit for this target in the diagnostics notebook.')",
        ]
    )

    return {
        "cells": [
            common_setup,
            load_cell,
            basic_target_cell,
            summary_cell,
            split_cell,
            missing_feature_cell,
            row_coverage_cell,
            missing_rows_cell,
            sample_rows_cell,
            correlation_cell,
            fit_cell,
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for target in TARGET_COLUMNS:
        notebook = build_notebook(target)
        output_path = OUTPUT_DIR / f"{target}_diagnostics.ipynb"
        output_path.write_text(json.dumps(notebook, indent=2))
        print(output_path)


if __name__ == "__main__":
    main()
