"""phase_1a_initial_schema

Revision ID: 20260409_0001
Revises:
Create Date: 2026-04-09 03:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260409_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "songs",
        sa.Column("song_id", sa.String(length=128), nullable=False),
        sa.Column("song_name", sa.String(length=512), nullable=False),
        sa.Column("artist_name", sa.String(length=512), nullable=False),
        sa.Column("genre", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("song_id", name="pk_songs"),
    )
    op.create_index("ix_songs_song_name", "songs", ["song_name"], unique=False)
    op.create_index("ix_songs_artist_name", "songs", ["artist_name"], unique=False)
    op.create_index("ix_songs_genre", "songs", ["genre"], unique=False)
    op.create_index("ix_songs_song_name_lower", "songs", [sa.text("lower(song_name)")], unique=False)
    op.create_index("ix_songs_artist_name_lower", "songs", [sa.text("lower(artist_name)")], unique=False)
    op.create_index("ix_songs_genre_lower", "songs", [sa.text("lower(genre)")], unique=False)

    op.create_table(
        "song_neighbors",
        sa.Column("source_song_id", sa.String(length=128), nullable=False),
        sa.Column("target_song_id", sa.String(length=128), nullable=False),
        sa.Column("neighbor_rank", sa.Integer(), nullable=False),
        sa.CheckConstraint("neighbor_rank BETWEEN 1 AND 5", name="ck_song_neighbors_rank_range"),
        sa.CheckConstraint("source_song_id <> target_song_id", name="ck_song_neighbors_not_self"),
        sa.ForeignKeyConstraint(
            ["source_song_id"],
            ["songs.song_id"],
            name="fk_song_neighbors_source_song_id_songs",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_song_id"],
            ["songs.song_id"],
            name="fk_song_neighbors_target_song_id_songs",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("source_song_id", "neighbor_rank", name="pk_song_neighbors"),
        sa.UniqueConstraint("source_song_id", "target_song_id", name="uq_song_neighbors_source_target"),
    )
    op.create_index(
        "ix_song_neighbors_source_song_id",
        "song_neighbors",
        ["source_song_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_song_neighbors_source_song_id", table_name="song_neighbors")
    op.drop_table("song_neighbors")

    op.drop_index("ix_songs_genre_lower", table_name="songs")
    op.drop_index("ix_songs_artist_name_lower", table_name="songs")
    op.drop_index("ix_songs_song_name_lower", table_name="songs")
    op.drop_index("ix_songs_genre", table_name="songs")
    op.drop_index("ix_songs_artist_name", table_name="songs")
    op.drop_index("ix_songs_song_name", table_name="songs")
    op.drop_table("songs")

