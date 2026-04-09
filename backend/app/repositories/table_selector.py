from __future__ import annotations

from app.db.models.song import Song
from app.db.models.song_neighbor import SongNeighbor
from app.db.models.staging_song import StagingSong
from app.db.models.staging_song_neighbor import StagingSongNeighbor


def get_song_model(read_from_stage: bool):
    return StagingSong if read_from_stage else Song


def get_song_neighbor_model(read_from_stage: bool):
    return StagingSongNeighbor if read_from_stage else SongNeighbor

