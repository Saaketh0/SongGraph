from .columns import IMPUTATION_TARGET_COLUMNS

XGBOOST_FEATURE_COLUMNS = [
    "duration_ms",
    "valence",
    "loudness",
    "danceability",
    "energy",
    "tempo",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "explicit",
    "key",
    "time_signature",
    "mode",
]

IMPUTATION_REGRESSION_TARGETS = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
]

IMPUTATION_CLASSIFICATION_TARGETS = [
    "key",
    "mode",
]


def get_initial_imputation_targets() -> list[str]:
    return list(IMPUTATION_TARGET_COLUMNS)


def get_xgboost_feature_columns() -> list[str]:
    return list(XGBOOST_FEATURE_COLUMNS)


def get_feature_columns_for_target(target_column: str) -> list[str]:
    return [column for column in XGBOOST_FEATURE_COLUMNS if column != target_column]
