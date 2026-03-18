"""Watch history model.

Tracks a user's viewing events for a movie.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class WatchHistory(BaseModel):
    __tablename__ = "watch_history"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id = Column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    watch_duration_seconds = Column(Integer, default=0, nullable=False)

    user = relationship("User")
    movie = relationship("Movie")

    def __repr__(self) -> str:
        return f"<WatchHistory user={self.user_id} movie={self.movie_id}>"
