"""phase_1b_stage_tables

Revision ID: 20260409_0002
Revises: 20260409_0001
Create Date: 2026-04-09 04:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260409_0002"
down_revision: Union[str, None] = "20260409_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "songs_stage",
        sa.Column("song_id", sa.String(length=128), nullable=False),
        sa.Column("song_name", sa.String(length=512), nullable=False),
        sa.Column("artist_name", sa.String(length=512), nullable=False),
        sa.Column("genre", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("song_id", name="pk_songs_stage"),
    )
    op.create_index("ix_songs_stage_song_name", "songs_stage", ["song_name"], unique=False)
    op.create_index("ix_songs_stage_artist_name", "songs_stage", ["artist_name"], unique=False)
    op.create_index("ix_songs_stage_genre", "songs_stage", ["genre"], unique=False)

    op.create_table(
        "song_neighbors_stage",
        sa.Column("source_song_id", sa.String(length=128), nullable=False),
        sa.Column("target_song_id", sa.String(length=128), nullable=False),
        sa.Column("neighbor_rank", sa.Integer(), nullable=False),
        sa.CheckConstraint("neighbor_rank BETWEEN 1 AND 5", name="ck_song_neighbors_stage_rank_range"),
        sa.CheckConstraint("source_song_id <> target_song_id", name="ck_song_neighbors_stage_not_self"),
        sa.ForeignKeyConstraint(
            ["source_song_id"],
            ["songs_stage.song_id"],
            name="fk_song_neighbors_stage_source_song_id_songs_stage",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_song_id"],
            ["songs_stage.song_id"],
            name="fk_song_neighbors_stage_target_song_id_songs_stage",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("source_song_id", "neighbor_rank", name="pk_song_neighbors_stage"),
        sa.UniqueConstraint("source_song_id", "target_song_id", name="uq_song_neighbors_stage_source_target"),
    )
    op.create_index(
        "ix_song_neighbors_stage_source_song_id",
        "song_neighbors_stage",
        ["source_song_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_song_neighbors_stage_source_song_id", table_name="song_neighbors_stage")
    op.drop_table("song_neighbors_stage")

    op.drop_index("ix_songs_stage_genre", table_name="songs_stage")
    op.drop_index("ix_songs_stage_artist_name", table_name="songs_stage")
    op.drop_index("ix_songs_stage_song_name", table_name="songs_stage")
    op.drop_table("songs_stage")

