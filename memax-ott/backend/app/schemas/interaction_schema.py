"""Interaction schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InteractionCreate(BaseModel):
    movie_id: int
    interaction_type: str = Field(..., max_length=50)
    rating: Optional[float] = Field(None, ge=0, le=10)
    interaction_value: float = Field(1.0, ge=0, le=10)


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    interaction_type: str
    rating: Optional[float]
    interaction_value: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class WatchProgressCreate(BaseModel):
    movie_id: int
    progress_seconds: int = Field(..., ge=0)
    progress_percentage: float = Field(..., ge=0, le=100)


class WatchProgressResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    progress_seconds: int
    progress_percentage: float
    last_watched_at: datetime
    
    class Config:
        from_attributes = True
