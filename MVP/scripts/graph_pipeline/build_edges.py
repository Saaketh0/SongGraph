from __future__ import annotations

import pandas as pd


def build_performs_edges(df: pd.DataFrame) -> list[dict]:
    edge_rows = df[["artist_id", "song_id"]].drop_duplicates().sort_values(by=["song_id"])
    return [
        {
            "source": row.artist_id,
            "target": row.song_id,
            "type": "PERFORMS",
        }
        for row in edge_rows.itertuples(index=False)
    ]
