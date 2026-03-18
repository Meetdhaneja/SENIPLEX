"""Movie model (minimal)."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Movie(BaseModel):
    __tablename__ = "movies"

    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    release_year = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    embeddings = relationship(
        "MovieEmbedding",
        back_populates="movie",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

