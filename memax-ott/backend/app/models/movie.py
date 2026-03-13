"""Movie model"""
from sqlalchemy import Column, String, Integer, Float, Text, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import BaseModel, Base

# Association tables for many-to-many relationships
movie_genres = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)

movie_countries = Table(
    'movie_countries',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    Column('country_id', Integer, ForeignKey('countries.id', ondelete='CASCADE'), primary_key=True)
)


class Movie(BaseModel):
    """Movie database model"""
    __tablename__ = "movies"
    
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    release_year = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    rating = Column(Float, default=0.0)
    imdb_rating = Column(Float, nullable=True)
    age_rating = Column(String(50), nullable=True)  # TV-MA, PG-13, etc.
    date_added = Column(String(100), nullable=True)
    content_type = Column(String(50), nullable=False)  # Movie, TV Show, Documentary
    director = Column(String(255), nullable=True)
    cast = Column(Text, nullable=True)  # Comma-separated
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    trailer_url = Column(String(500), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    
    # Relationships
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    countries = relationship("Country", secondary=movie_countries, back_populates="movies")
    watch_history = relationship("WatchHistory", back_populates="movie", cascade="all, delete-orphan")
    watch_progress = relationship("WatchProgress", back_populates="movie", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="movie", cascade="all, delete-orphan")
    embeddings = relationship("MovieEmbedding", back_populates="movie", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie {self.title}>"
