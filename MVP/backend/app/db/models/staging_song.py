from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingSong(Base):
    __tablename__ = "songs_stage"

    song_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    song_name: Mapped[str] = mapped_column(String(512), nullable=False)
    artist_name: Mapped[str] = mapped_column(String(512), nullable=False)
    genre: Mapped[str] = mapped_column(String(256), nullable=False)

