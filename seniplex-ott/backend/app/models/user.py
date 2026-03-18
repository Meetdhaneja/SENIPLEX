"""User model (minimal)."""

from __future__ import annotations

from sqlalchemy import Column, String

from app.db.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
