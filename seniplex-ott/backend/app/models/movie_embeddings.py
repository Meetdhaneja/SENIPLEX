"""Movie embeddings model."""

from __future__ import annotations

from typing import Any, Optional, cast

from sqlalchemy import Column, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class MovieEmbedding(BaseModel):
    __tablename__ = "movie_embeddings"

    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # NOTE: We cast Column[...] to the Python value type so static type checkers
    # (e.g. Pyright) understand assignments like `movie_emb.content_embedding = [...]`.
    content_embedding: Optional[list[float]] = cast(Any, Column(JSON, nullable=True))
    collaborative_embedding: Optional[list[float]] = cast(Any, Column(JSON, nullable=True))

    faiss_index_id = Column(Integer, nullable=True)

    movie = relationship("Movie", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<MovieEmbedding movie_id={self.movie_id}>"
