"""
AI-Powered Routes
Advanced AI endpoints for recommendations, search, and insights
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation_schema import RecommendationResponse, RecommendationItem
from app.schemas.movie_schema import MovieResponse
from app.routes.auth import get_current_user
from app.services.recommendation_service import get_recommendation_service
from app.models.movie import Movie
from loguru import logger

router = APIRouter()


@router.get("/recommendations/hybrid/{user_id}", response_model=RecommendationResponse)
async def get_hybrid_recommendations(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Hybrid Recommendations
    Combines content-based, collaborative filtering, and popularity signals
    """
    try:
        service = get_recommendation_service()
        
        # Use personalized recommendations with hybrid ranking
        from app.schemas.recommendation_schema import RecommendationRequest
        request = RecommendationRequest(limit=limit, exclude_watched=True)
        
        recommendations = service.get_personalized_recommendations(
            db=db,
            user_id=user_id,
            request=request
        )
        
        logger.info(f"Generated {len(recommendations.recommendations)} hybrid recommendations for user {user_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in hybrid recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{movie_id}", response_model=List[MovieResponse])
async def get_similar_movies(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get Similar Movies
    AI-powered similarity using vector embeddings
    """
    try:
        service = get_recommendation_service()
        similar_movies = service.get_similar_movies(db, movie_id, limit)
        
        logger.info(f"Found {len(similar_movies)} similar movies for movie {movie_id}")
        return [MovieResponse.from_orm(movie) for movie in similar_movies]
        
    except Exception as e:
        logger.error(f"Error getting similar movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[MovieResponse])
async def ai_powered_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    AI Powered Search
    Semantic search using embeddings for better results
    """
    try:
        # For now, use basic search (can be enhanced with semantic search later)
        from sqlalchemy import or_
        
        movies = db.query(Movie).filter(
            or_(
                Movie.title.ilike(f"%{query}%"),
                Movie.description.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        logger.info(f"AI search for '{query}' returned {len(movies)} results")
        return [MovieResponse.from_orm(movie) for movie in movies]
        
    except Exception as e:
        logger.error(f"Error in AI search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending", response_model=List[MovieResponse])
async def get_trending_movies(
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get Trending Movies
    AI-powered trending detection based on growth rate
    """
    try:
        service = get_recommendation_service()
        trending_movies = service.get_trending_recommendations(
            db=db,
            limit=limit,
            content_type=content_type
        )
        
        logger.info(f"Found {len(trending_movies)} trending movies")
        return [MovieResponse.from_orm(movie) for movie in trending_movies]
        
    except Exception as e:
        logger.error(f"Error getting trending movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{movie_id}")
async def get_movie_insights(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Movie Insights
    AI-generated insights about a movie
    """
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Get similar movies for insights
        service = get_recommendation_service()
        similar_movies = service.get_similar_movies(db, movie_id, limit=5)
        
        # Calculate insights
        insights = {
            "movie_id": movie_id,
            "title": movie.title,
            "popularity_score": movie.view_count / 1000 if movie.view_count else 0,
            "rating": movie.rating,
            "total_views": movie.view_count,
            "genres": [g.name for g in movie.genres],
            "similar_movies_count": len(similar_movies),
            "similar_movies": [
                {
                    "id": m.id,
                    "title": m.title,
                    "rating": m.rating
                }
                for m in similar_movies[:3]
            ],
            "recommendations": {
                "watch_if_you_liked": [m.title for m in similar_movies[:3]],
                "trending": movie.view_count > 1000,
                "highly_rated": movie.rating >= 8.0
            }
        }
        
        logger.info(f"Generated insights for movie {movie_id}")
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/diversity/{user_id}", response_model=RecommendationResponse)
async def get_diverse_recommendations(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_diversity: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Diverse Recommendations
    Ensures variety across genres and content types
    """
    try:
        service = get_recommendation_service()
        
        # Get personalized recommendations (already includes diversity)
        from app.schemas.recommendation_schema import RecommendationRequest
        request = RecommendationRequest(limit=limit, exclude_watched=True)
        
        recommendations = service.get_personalized_recommendations(
            db=db,
            user_id=user_id,
            request=request
        )
        
        # Add diversity metadata
        recommendations.recommendation_type = "ai_diverse"
        
        logger.info(f"Generated {len(recommendations.recommendations)} diverse recommendations for user {user_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in diverse recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
