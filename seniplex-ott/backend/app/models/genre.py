"""Genre model (minimal)."""

from __future__ import annotations

from sqlalchemy import Column, String

from app.db.base import BaseModel


class Genre(BaseModel):
    __tablename__ = "genres"

    name = Column(String(255), unique=True, index=True, nullable=False)
