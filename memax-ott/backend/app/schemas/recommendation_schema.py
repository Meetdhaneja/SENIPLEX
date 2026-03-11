"""Recommendation schemas"""
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.movie_schema import MovieResponse


class RecommendationRequest(BaseModel):
    limit: int = 20
    exclude_watched: bool = True
    genres: Optional[List[int]] = None


class RecommendationItem(BaseModel):
    movie: MovieResponse
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    recommendation_type: str
