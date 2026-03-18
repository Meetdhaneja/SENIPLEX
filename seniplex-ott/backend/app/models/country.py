"""Country model (minimal)."""

from __future__ import annotations

from sqlalchemy import Column, String

from app.db.base import BaseModel


class Country(BaseModel):
    __tablename__ = "countries"

    name = Column(String(200), nullable=False, unique=True, index=True)
