"""Recommendation routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation_schema import RecommendationResponse, RecommendationRequest
from app.schemas.movie_schema import MovieResponse
from app.services.recommendation_service import (
    get_personalized_recommendations,
    get_similar_movies,
    get_cold_start_recommendations
)
from app.routes.auth import get_current_user

router = APIRouter()


@router.post("/personalized", response_model=RecommendationResponse)
def get_personalized(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized recommendations"""
    return get_personalized_recommendations(db, current_user.id, request)


@router.get("/similar/{movie_id}", response_model=List[MovieResponse])
def get_similar(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get similar movies"""
    return get_similar_movies(db, movie_id, limit)


@router.get("/cold-start", response_model=List[MovieResponse])
def get_cold_start(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cold start recommendations for new users"""
    return get_cold_start_recommendations(db, current_user.id, limit)


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations_for_user(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    exclude_watched: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Recommendations for specific user
    Returns personalized recommendations for the given user ID
    """
    request = RecommendationRequest(
        limit=limit,
        exclude_watched=exclude_watched
    )
    return get_personalized_recommendations(db, user_id, request)
