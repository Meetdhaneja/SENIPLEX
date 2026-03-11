"""Admin schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_movies: int
    total_views: int
    total_interactions: int


class AdminUserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    total_watch_time: int
    total_interactions: int


class AdminMovieStats(BaseModel):
    id: int
    title: str
    view_count: int
    rating: float
    total_watch_time: int
    unique_viewers: int
