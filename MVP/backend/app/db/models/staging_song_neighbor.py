from sqlalchemy import CheckConstraint, ForeignKey, Integer, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingSongNeighbor(Base):
    __tablename__ = "song_neighbors_stage"
    __table_args__ = (
        PrimaryKeyConstraint("source_song_id", "neighbor_rank", name="pk_song_neighbors_stage"),
        UniqueConstraint("source_song_id", "target_song_id", name="uq_song_neighbors_stage_source_target"),
        CheckConstraint("neighbor_rank BETWEEN 1 AND 5", name="ck_song_neighbors_stage_rank_range"),
        CheckConstraint("source_song_id <> target_song_id", name="ck_song_neighbors_stage_not_self"),
    )

    source_song_id: Mapped[str] = mapped_column(
        ForeignKey("songs_stage.song_id", ondelete="CASCADE"),
        nullable=False,
    )
    target_song_id: Mapped[str] = mapped_column(
        ForeignKey("songs_stage.song_id", ondelete="RESTRICT"),
        nullable=False,
    )
    neighbor_rank: Mapped[int] = mapped_column(Integer, nullable=False)

