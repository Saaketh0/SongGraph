IDENTITY_COLUMNS = [
    "track_id",
    "artist_name",
    "track_name",
]

AUDIO_NUMERIC_COLUMNS = [
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
]

AUDIO_CATEGORICAL_COLUMNS = [
    "explicit",
    "key",
    "time_signature",
    "mode",
]

IMPUTATION_TARGET_COLUMNS = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "key",
    "mode",
]

ALL_COLUMNS = [
    "artist_name",
    "track_name",
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
    "track_id",
    "mode",
]

TEXT_COLUMNS = [
    "artist_name",
    "track_name",
    "track_id",
]

TRACK_ID_FILL_COLUMNS = [
    column for column in ALL_COLUMNS if column != "track_id"
]

ARTIST_TRACK_FILL_COLUMNS = [
    column for column in ALL_COLUMNS if column not in {"artist_name", "track_name"}
]


def get_column_groups() -> dict[str, list[str]]:
    return {
        "identity": IDENTITY_COLUMNS,
        "audio_numeric": AUDIO_NUMERIC_COLUMNS,
        "audio_categorical": AUDIO_CATEGORICAL_COLUMNS,
    }
