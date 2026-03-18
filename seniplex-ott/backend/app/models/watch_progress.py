"""Watch progress model.

Keeps track of how far a user has watched a movie.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class WatchProgress(BaseModel):
    __tablename__ = "watch_progress"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id = Column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    progress_seconds = Column(Integer, default=0, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    last_watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
    movie = relationship("Movie")
