"""User features model for recommendation/ML pipelines.

This module exists so imports like `from app.models import UserFeatures` (or
`from .user_features import UserFeatures` inside the models package) resolve
cleanly during type-checking, even if the wider feature pipeline is still WIP.
"""

from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class UserFeatures(BaseModel):
    __tablename__ = "user_features"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    favorite_genres = Column(JSON, nullable=True)
    favorite_actors = Column(JSON, nullable=True)
    favorite_directors = Column(JSON, nullable=True)

    avg_watch_duration = Column(Float, default=0.0)
    total_watch_time = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)

    user_embedding = Column(JSON, nullable=True)

    # Keep relationship unidirectional by default; the `User` model in this
    # codebase is intentionally minimal and may not define `user_features`.
    user = relationship("User")
