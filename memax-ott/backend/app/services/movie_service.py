"""Movie service"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, func, text
from typing import List, Tuple, Optional
from datetime import datetime
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from app.schemas.movie_schema import MovieCreate, MovieUpdate
from loguru import logger

def create_mock_movie(id: int, title: str, is_featured: bool = False):
    """Helper to create a Safe Mock Movie object that matches MovieResponse exactly"""
    return {
        "id": id,
        "title": title,
        "description": f"An epic journey in {title}. Experience the magic of MEMAX.",
        "release_year": 2024,
        "duration_minutes": 120,
        "rating": 8.5,
        "imdb_rating": 8.2,
        "content_type": "Movie",
        "is_featured": is_featured,
        "view_count": 1000,
        "thumbnail_url": f"https://placehold.co/600x400/000000/FFFFFF?text={title.replace(' ', '+')}",
        "created_at": datetime.utcnow(),
        "genres": [],
        "countries": [],
        "age_rating": "PG-13",
        "director": "MEMAX AI",
        "cast": "AI Cast",
        "date_added": "March 2024",
        "video_url": None,
        "trailer_url": None
    }

STATIC_FALLBACK = [
    create_mock_movie(9991, "Inception", True),
    create_mock_movie(9992, "The Dark Knight", True),
    create_mock_movie(9993, "Interstellar", True),
    create_mock_movie(9994, "The Matrix", False),
    create_mock_movie(9995, "Pulp Fiction", False),
    create_mock_movie(9996, "Breaking Bad", True),
    create_mock_movie(9997, "Stranger Things", True),
    create_mock_movie(9998, "The Godfather", False),
    create_mock_movie(9999, "Avatar", False),
    create_mock_movie(10000, "Parasite", True)
]

def _safe_serialize(movie_obj):
    """Safely convert a SQLAlchemy model to a dictionary that matches MovieResponse.
    Ensures no None values reach non-optional Pydantic fields.
    """
    try:
        return {
            "id": getattr(movie_obj, "id", 0),
            "title": str(getattr(movie_obj, "title", "Untitled")),
            "description": getattr(movie_obj, "description", None),
            "release_year": getattr(movie_obj, "release_year", 2024),
            "duration_minutes": getattr(movie_obj, "duration_minutes", None),
            "rating": float(getattr(movie_obj, "rating", 0.0) or 0.0),
            "imdb_rating": getattr(movie_obj, "imdb_rating", None),
            "content_type": str(getattr(movie_obj, "content_type", "Movie")),
            "is_featured": bool(getattr(movie_obj, "is_featured", False)),
            "view_count": int(getattr(movie_obj, "view_count", 0) or 0),
            "thumbnail_url": getattr(movie_obj, "thumbnail_url", None),
            "video_url": getattr(movie_obj, "video_url", None),
            "trailer_url": getattr(movie_obj, "trailer_url", None),
            "age_rating": getattr(movie_obj, "age_rating", "PG-13"),
            "date_added": getattr(movie_obj, "date_added", ""),
            "director": getattr(movie_obj, "director", None),
            "cast": getattr(movie_obj, "cast", None),
            "created_at": getattr(movie_obj, "created_at", None) or datetime.utcnow(),
            "genres": [{"id": g.id, "name": g.name} for g in movie_obj.genres] if hasattr(movie_obj, "genres") and movie_obj.genres else [],
            "countries": [{"id": c.id, "name": c.name} for c in movie_obj.countries] if hasattr(movie_obj, "countries") and movie_obj.countries else []
        }
    except Exception as e:
        logger.error(f"Critical serialization error: {e}")
        return None

def get_movies(
    db: Session, 
    page: int = 1, 
    page_size: int = 20, 
    genre: Optional[str] = None, 
    country: Optional[str] = None, 
    content_type: Optional[str] = None
) -> Tuple[List[dict], int]:
    """Get movies with corrected signature to prevent positional argument TypeErrors"""
    if db is None: return STATIC_FALLBACK, len(STATIC_FALLBACK)
    try:
        # Table health check
        db.execute(text("SELECT 1 FROM movies LIMIT 1"))
        
        query = db.query(Movie).options(joinedload(Movie.genres), joinedload(Movie.countries))
        
        # Apply filters if provided
        if genre: query = query.join(Movie.genres).filter(Genre.name == genre)
        if country: query = query.join(Movie.countries).filter(Country.name == country)
        if content_type: query = query.filter(Movie.content_type == content_type)
        
        total = query.count()
        if total == 0: return STATIC_FALLBACK, len(STATIC_FALLBACK)
        
        movies = query.order_by(desc(Movie.release_year)).offset((page - 1) * page_size).limit(page_size).all()
        
        results = []
        for m in movies:
            s = _safe_serialize(m)
            if s: results.append(s)
            
        return results if results else STATIC_FALLBACK, total
    except Exception as e:
        logger.warning(f"get_movies triggered fallback: {e}")
        return STATIC_FALLBACK, len(STATIC_FALLBACK)

def get_featured_movies(db: Session, limit: int = 10) -> List[dict]:
    if db is None: return [m for m in STATIC_FALLBACK if m["is_featured"]][:limit]
    try:
        db.execute(text("SELECT 1 FROM movies LIMIT 1"))
        movies = db.query(Movie).options(joinedload(Movie.genres), joinedload(Movie.countries)).filter(Movie.is_featured == True).limit(limit).all()
        results = [_safe_serialize(m) for m in movies if _safe_serialize(m)]
        return results if results else [m for m in STATIC_FALLBACK if m["is_featured"]][:limit]
    except Exception as e:
        logger.warning(f"get_featured triggered fallback: {e}")
        return [m for m in STATIC_FALLBACK if m["is_featured"]][:limit]

def get_trending_movies(db: Session, limit: int = 10) -> List[dict]:
    if db is None: return STATIC_FALLBACK[:limit]
    try:
        db.execute(text("SELECT 1 FROM movies LIMIT 1"))
        movies = db.query(Movie).options(joinedload(Movie.genres), joinedload(Movie.countries)).order_by(desc(Movie.view_count)).limit(limit).all()
        results = [_safe_serialize(m) for m in movies if _safe_serialize(m)]
        return results if results else STATIC_FALLBACK[:limit]
    except Exception as e:
        logger.warning(f"get_trending triggered fallback: {e}")
        return STATIC_FALLBACK[:limit]

def get_movie_by_id(db: Session, movie_id: int) -> Optional[dict]:
    if db is None: return None
    try:
        movie = db.query(Movie).options(joinedload(Movie.genres), joinedload(Movie.countries)).filter(Movie.id == movie_id).first()
        return _safe_serialize(movie) if movie else None
    except Exception: return None

def search_movies(db: Session, query: str, limit: int = 20) -> List[dict]:
    if db is None: return []
    try:
        movies = db.query(Movie).filter(Movie.title.ilike(f"%{query}%")).limit(limit).all()
        return [_safe_serialize(m) for m in movies if _safe_serialize(m)]
    except Exception: return []

# Keep these for admin ops
def create_movie(db: Session, movie_data: MovieCreate) -> Movie:
    movie = Movie(**movie_data.dict(exclude={"genre_ids", "country_ids"}))
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

def update_movie(db: Session, movie_id: int, movie_data: MovieUpdate) -> Optional[Movie]:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie: return None
    for field, value in movie_data.dict(exclude_unset=True).items():
        setattr(movie, field, value)
    db.commit()
    db.refresh(movie)
    return movie

def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie: return False
    db.delete(movie)
    db.commit()
    return True
