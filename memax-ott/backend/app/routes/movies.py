"""Movie routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.db.session import get_db
from app.models.user import User
from app.models.movie import Movie
from app.schemas.movie_schema import MovieResponse, MovieListResponse, MovieCreate, MovieUpdate
from app.services.movie_service import (
    get_movies, get_movie_by_id, create_movie, update_movie,
    delete_movie, search_movies, get_featured_movies, get_trending_movies
)
from app.routes.auth import get_current_user

router = APIRouter()


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    country: Optional[str] = None,
    content_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List movies with pagination and filters"""
    movies, total = get_movies(db, page, page_size, genre, country, content_type)
    return {
        "movies": movies,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/count")
def get_movie_count(db: Session = Depends(get_db)):
    """Get total number of movies in the database"""
    return {"count": db.query(Movie).count()}


@router.get("/featured", response_model=List[MovieResponse])
def list_featured_movies(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get featured movies"""
    return get_featured_movies(db, limit)


@router.get("/trending", response_model=List[MovieResponse])
def list_trending_movies(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get trending movies"""
    return get_trending_movies(db, limit)


@router.get("/search", response_model=List[MovieResponse])
def search_movies_endpoint(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search movies"""
    return search_movies(db, q, limit)


@router.get("/stream/{filename}")
def stream_movie(filename: str):
    """Internal streaming endpoint for uploaded files"""
    file_path = f"uploads/movies/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(file_path, media_type="video/mp4")


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get movie by ID"""
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie_endpoint(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new movie (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return create_movie(db, movie_data)


@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie_endpoint(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update movie (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    movie = update_movie(db, movie_id, movie_data)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_endpoint(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    """Delete movie (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    success = delete_movie(db, movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
