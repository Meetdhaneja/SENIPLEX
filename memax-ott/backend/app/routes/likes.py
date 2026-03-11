"""
Likes Routes
Movie like/unlike functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.movie import Movie
from app.models.interaction import Interaction
from app.schemas.movie_schema import MovieResponse
from app.routes.auth import get_current_user
from loguru import logger
from datetime import datetime

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def like_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Like Movie Endpoint
    Add a movie to user's liked list
    """
    try:
        # Check if movie exists
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        # Check if already liked
        existing_like = db.query(Interaction).filter(
            Interaction.user_id == current_user.id,
            Interaction.movie_id == movie_id,
            Interaction.interaction_type == "like"
        ).first()
        
        if existing_like:
            return {
                "message": "Movie already liked",
                "movie_id": movie_id,
                "already_liked": True
            }
        
        # Create like interaction
        like = Interaction(
            user_id=current_user.id,
            movie_id=movie_id,
            interaction_type="like",
            interaction_value=1.0,
            timestamp=datetime.utcnow()
        )
        db.add(like)
        db.commit()
        
        logger.info(f"User {current_user.id} liked movie {movie_id}")
        
        return {
            "message": "Movie liked successfully",
            "movie_id": movie_id,
            "movie_title": movie.title,
            "already_liked": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking movie: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{movie_id}", status_code=status.HTTP_200_OK)
async def unlike_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unlike Movie Endpoint
    Remove a movie from user's liked list
    """
    try:
        # Find the like interaction
        like = db.query(Interaction).filter(
            Interaction.user_id == current_user.id,
            Interaction.movie_id == movie_id,
            Interaction.interaction_type == "like"
        ).first()
        
        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Like not found"
            )
        
        # Delete the like
        db.delete(like)
        db.commit()
        
        logger.info(f"User {current_user.id} unliked movie {movie_id}")
        
        return {
            "message": "Movie unliked successfully",
            "movie_id": movie_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking movie: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=List[MovieResponse])
async def get_my_likes(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    My Likes
    Get all movies liked by the current user
    """
    try:
        # Get all liked movie IDs
        liked_interactions = db.query(Interaction).filter(
            Interaction.user_id == current_user.id,
            Interaction.interaction_type == "like"
        ).offset(skip).limit(limit).all()
        
        movie_ids = [interaction.movie_id for interaction in liked_interactions]
        
        # Fetch movies
        movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
        
        logger.info(f"User {current_user.id} retrieved {len(movies)} liked movies")
        
        return [MovieResponse.from_orm(movie) for movie in movies]
        
    except Exception as e:
        logger.error(f"Error getting liked movies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
