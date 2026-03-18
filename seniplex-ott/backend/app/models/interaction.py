"""Interaction model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Interaction(BaseModel):
    """User-Movie interaction database model."""

    __tablename__ = "interactions"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id = Column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    interaction_type = Column(String(50), nullable=False)  # view, like, dislike, search, click
    rating = Column(Float, nullable=True)
    interaction_value = Column(Float, default=1.0, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Optional relationships (safe even if back_populates not defined on User/Movie)
    user = relationship("User")
    movie = relationship("Movie")

    def __repr__(self) -> str:
        return (
            f"<Interaction user={self.user_id} movie={self.movie_id} "
            f"type={self.interaction_type}>"
        )
