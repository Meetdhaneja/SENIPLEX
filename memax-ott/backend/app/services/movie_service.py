"""Movie service"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Tuple, Optional
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from app.schemas.movie_schema import MovieCreate, MovieUpdate


def get_movies(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    genre: Optional[str] = None,
    country: Optional[str] = None,
    content_type: Optional[str] = None
) -> Tuple[List[Movie], int]:
    """Get movies with pagination and filters"""
    query = db.query(Movie)
    
    if genre:
        query = query.join(Movie.genres).filter(Genre.name == genre)
    if country:
        query = query.join(Movie.countries).filter(Country.name == country)
    if content_type:
        query = query.filter(Movie.content_type == content_type)
    
    total = query.count()
    movies = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return movies, total


def get_movie_by_id(db: Session, movie_id: int) -> Optional[Movie]:
    """Get movie by ID"""
    return db.query(Movie).filter(Movie.id == movie_id).first()


def create_movie(db: Session, movie_data: MovieCreate) -> Movie:
    """Create new movie"""
    movie = Movie(**movie_data.dict(exclude={"genre_ids", "country_ids"}))
    
    if movie_data.genre_ids:
        genres = db.query(Genre).filter(Genre.id.in_(movie_data.genre_ids)).all()
        movie.genres = genres
    
    if movie_data.country_ids:
        countries = db.query(Country).filter(Country.id.in_(movie_data.country_ids)).all()
        movie.countries = countries
    
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(db: Session, movie_id: int, movie_data: MovieUpdate) -> Optional[Movie]:
    """Update movie"""
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        return None
    
    update_data = movie_data.dict(exclude_unset=True, exclude={"genre_ids", "country_ids"})
    for field, value in update_data.items():
        setattr(movie, field, value)
    
    if movie_data.genre_ids is not None:
        genres = db.query(Genre).filter(Genre.id.in_(movie_data.genre_ids)).all()
        movie.genres = genres
    
    if movie_data.country_ids is not None:
        countries = db.query(Country).filter(Country.id.in_(movie_data.country_ids)).all()
        movie.countries = countries
    
    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie_id: int) -> bool:
    """Delete movie"""
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        return False
    db.delete(movie)
    db.commit()
    return True


def search_movies(db: Session, query: str, limit: int = 20) -> List[Movie]:
    """Search movies"""
    search_filters = [Movie.title.ilike(f"%{query}%"), Movie.description.ilike(f"%{query}%")]
    # Check if model has cast/director fields before querying
    if hasattr(Movie, 'cast'):
        search_filters.append(Movie.cast.ilike(f"%{query}%"))
    if hasattr(Movie, 'director'):
        search_filters.append(Movie.director.ilike(f"%{query}%"))

    return db.query(Movie).filter(or_(*search_filters)).limit(limit).all()


def get_featured_movies(db: Session, limit: int = 10) -> List[Movie]:
    """Get featured movies"""
    return db.query(Movie).filter(Movie.is_featured == True).limit(limit).all()


def get_trending_movies(db: Session, limit: int = 10) -> List[Movie]:
    """Get trending movies"""
    return db.query(Movie).order_by(desc(Movie.view_count)).limit(limit).all()
