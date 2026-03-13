"""Movie schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GenreBase(BaseModel):
    name: str


class GenreResponse(GenreBase):
    id: int
    
    class Config:
        from_attributes = True


class CountryBase(BaseModel):
    name: str


class CountryResponse(CountryBase):
    id: int
    
    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    release_year: Optional[int] = None
    duration_minutes: Optional[int] = None
    content_type: str = Field(..., max_length=50)
    director: Optional[str] = None
    cast: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    trailer_url: Optional[str] = None
    age_rating: Optional[str] = None


class MovieCreate(MovieBase):
    genre_ids: List[int] = []
    country_ids: List[int] = []


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    duration_minutes: Optional[int] = None
    rating: Optional[float] = None
    is_featured: Optional[bool] = None
    genre_ids: Optional[List[int]] = None
    country_ids: Optional[List[int]] = None


class MovieResponse(MovieBase):
    id: int
    rating: float
    imdb_rating: Optional[float]
    is_featured: bool
    view_count: int
    genres: List[GenreResponse] = []
    countries: List[CountryResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    movies: List[MovieResponse]
    total: int
    page: int
    page_size: int
