"""Recommendation log model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class RecommendationLog(BaseModel):
    __tablename__ = "recommendation_logs"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movie_id = Column(Integer, nullable=False)

    recommendation_type = Column(String(100), nullable=False)
    score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)

    context = Column(JSON, nullable=True)

    was_clicked = Column(Integer, default=0)
    was_watched = Column(Integer, default=0)
    watch_duration = Column(Integer, default=0)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Keep this relationship unidirectional to avoid requiring changes
    # in the existing `User` model in this codebase.
    user = relationship("User")
