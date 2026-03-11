"""
MEMAX OTT Platform - Complete Project Setup Script
This script generates all remaining files for the project
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# File contents dictionary
FILES = {
    # Schemas
    "app/schemas/user_schema.py": '''"""User schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    profile_picture: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
''',

    "app/schemas/movie_schema.py": '''"""Movie schemas"""
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
''',

    "app/schemas/interaction_schema.py": '''"""Interaction schemas"""
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
''',

    "app/schemas/recommendation_schema.py": '''"""Recommendation schemas"""
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
''',

    "app/schemas/admin_schema.py": '''"""Admin schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_movies: int
    total_views: int
    total_interactions: int


class AdminUserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    total_watch_time: int
    total_interactions: int


class AdminMovieStats(BaseModel):
    id: int
    title: str
    view_count: int
    rating: float
    total_watch_time: int
    unique_viewers: int
''',

    # Routes
    "app/routes/auth.py": '''"""Authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, Token, UserLogin
from app.core.security import verify_password, get_password_hash
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.services.user_service import create_user, get_user_by_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
''',

    "app/routes/movies.py": '''"""Movie routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.schemas.movie_schema import MovieResponse, MovieListResponse, MovieCreate, MovieUpdate
from app.services.movie_service import (
    get_movies, get_movie_by_id, create_movie, update_movie,
    delete_movie, search_movies, get_featured_movies, get_trending_movies
)
from app.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=MovieListResponse)
async def list_movies(
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


@router.get("/featured", response_model=List[MovieResponse])
async def list_featured_movies(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get featured movies"""
    return get_featured_movies(db, limit)


@router.get("/trending", response_model=List[MovieResponse])
async def list_trending_movies(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get trending movies"""
    return get_trending_movies(db, limit)


@router.get("/search", response_model=List[MovieResponse])
async def search_movies_endpoint(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search movies"""
    return search_movies(db, q, limit)


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get movie by ID"""
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie_endpoint(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new movie (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return create_movie(db, movie_data)


@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie_endpoint(
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
async def delete_movie_endpoint(
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
''',

    "app/routes/interactions.py": '''"""Interaction routes"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.interaction_schema import (
    InteractionCreate, InteractionResponse,
    WatchProgressCreate, WatchProgressResponse
)
from app.services.interaction_service import (
    create_interaction, get_user_interactions,
    create_or_update_watch_progress, get_user_watch_progress
)
from app.routes.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def record_interaction(
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record user interaction with movie"""
    return create_interaction(db, current_user.id, interaction_data)


@router.get("/", response_model=List[InteractionResponse])
async def list_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's interactions"""
    return get_user_interactions(db, current_user.id)


@router.post("/progress", response_model=WatchProgressResponse)
async def update_watch_progress(
    progress_data: WatchProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update watch progress"""
    return create_or_update_watch_progress(db, current_user.id, progress_data)


@router.get("/progress", response_model=List[WatchProgressResponse])
async def list_watch_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's watch progress (continue watching)"""
    return get_user_watch_progress(db, current_user.id)
''',

    "app/routes/recommendations.py": '''"""Recommendation routes"""
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
async def get_personalized(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized recommendations"""
    return get_personalized_recommendations(db, current_user.id, request)


@router.get("/similar/{movie_id}", response_model=List[MovieResponse])
async def get_similar(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get similar movies"""
    return get_similar_movies(db, movie_id, limit)


@router.get("/cold-start", response_model=List[MovieResponse])
async def get_cold_start(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cold start recommendations for new users"""
    return get_cold_start_recommendations(db, current_user.id, limit)
''',

    "app/routes/analytics.py": '''"""Analytics routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.models.user import User
from app.routes.auth import get_current_user

router = APIRouter()


@router.get("/user-stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user statistics"""
    from app.models.watch_history import WatchHistory
    from app.models.interaction import Interaction
    
    total_watched = db.query(WatchHistory).filter(WatchHistory.user_id == current_user.id).count()
    total_interactions = db.query(Interaction).filter(Interaction.user_id == current_user.id).count()
    
    return {
        "total_watched": total_watched,
        "total_interactions": total_interactions,
        "user_id": current_user.id
    }
''',

    "app/routes/admin.py": '''"""Admin routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_schema import AdminStats, AdminUserResponse
from app.services.admin_service import get_admin_stats, get_all_users
from app.routes.auth import get_current_user

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin access"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get platform statistics"""
    return get_admin_stats(db)


@router.get("/users", response_model=List[AdminUserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users"""
    return get_all_users(db)
''',

    # Services
    "app/services/user_service.py": '''"""User service"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_features import UserFeatures
from app.schemas.user_schema import UserCreate
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create new user"""
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create user features
    user_features = UserFeatures(user_id=user.id)
    db.add(user_features)
    db.commit()
    
    return user
''',

    "app/services/movie_service.py": '''"""Movie service"""
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
    return db.query(Movie).filter(
        or_(
            Movie.title.ilike(f"%{query}%"),
            Movie.description.ilike(f"%{query}%"),
            Movie.cast.ilike(f"%{query}%"),
            Movie.director.ilike(f"%{query}%")
        )
    ).limit(limit).all()


def get_featured_movies(db: Session, limit: int = 10) -> List[Movie]:
    """Get featured movies"""
    return db.query(Movie).filter(Movie.is_featured == True).limit(limit).all()


def get_trending_movies(db: Session, limit: int = 10) -> List[Movie]:
    """Get trending movies"""
    return db.query(Movie).order_by(desc(Movie.view_count)).limit(limit).all()
''',

    "app/services/interaction_service.py": '''"""Interaction service"""
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.interaction import Interaction
from app.models.watch_progress import WatchProgress
from app.models.watch_history import WatchHistory
from app.schemas.interaction_schema import InteractionCreate, WatchProgressCreate


def create_interaction(db: Session, user_id: int, interaction_data: InteractionCreate) -> Interaction:
    """Create interaction"""
    interaction = Interaction(
        user_id=user_id,
        **interaction_data.dict()
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_user_interactions(db: Session, user_id: int, limit: int = 100) -> List[Interaction]:
    """Get user interactions"""
    return db.query(Interaction).filter(Interaction.user_id == user_id).order_by(Interaction.timestamp.desc()).limit(limit).all()


def create_or_update_watch_progress(db: Session, user_id: int, progress_data: WatchProgressCreate) -> WatchProgress:
    """Create or update watch progress"""
    progress = db.query(WatchProgress).filter(
        WatchProgress.user_id == user_id,
        WatchProgress.movie_id == progress_data.movie_id
    ).first()
    
    if progress:
        progress.progress_seconds = progress_data.progress_seconds
        progress.progress_percentage = progress_data.progress_percentage
        progress.last_watched_at = datetime.utcnow()
    else:
        progress = WatchProgress(
            user_id=user_id,
            **progress_data.dict()
        )
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    return progress


def get_user_watch_progress(db: Session, user_id: int) -> List[WatchProgress]:
    """Get user watch progress"""
    return db.query(WatchProgress).filter(
        WatchProgress.user_id == user_id,
        WatchProgress.progress_percentage < 95
    ).order_by(WatchProgress.last_watched_at.desc()).all()
''',

    "app/services/recommendation_service.py": '''"""Recommendation service"""
from sqlalchemy.orm import Session
from typing import List
from app.models.movie import Movie
from app.models.interaction import Interaction
from app.schemas.recommendation_schema import RecommendationRequest, RecommendationResponse, RecommendationItem
from app.schemas.movie_schema import MovieResponse
from sqlalchemy import desc, func
import random


def get_personalized_recommendations(db: Session, user_id: int, request: RecommendationRequest) -> RecommendationResponse:
    """Get personalized recommendations"""
    # Get user's watched movies
    watched_movie_ids = []
    if request.exclude_watched:
        watched_movie_ids = [i.movie_id for i in db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.interaction_type == "view"
        ).all()]
    
    # Get recommendations (simplified - in production use AI engine)
    query = db.query(Movie)
    if watched_movie_ids:
        query = query.filter(~Movie.id.in_(watched_movie_ids))
    
    movies = query.order_by(desc(Movie.rating)).limit(request.limit).all()
    
    recommendations = [
        RecommendationItem(
            movie=MovieResponse.from_orm(movie),
            score=movie.rating / 10.0,
            reason="Based on your preferences"
        )
        for movie in movies
    ]
    
    return RecommendationResponse(
        recommendations=recommendations,
        recommendation_type="personalized"
    )


def get_similar_movies(db: Session, movie_id: int, limit: int = 10) -> List[Movie]:
    """Get similar movies"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return []
    
    # Get movies with similar genres (simplified)
    genre_ids = [g.id for g in movie.genres]
    if not genre_ids:
        return []
    
    similar = db.query(Movie).join(Movie.genres).filter(
        Movie.id != movie_id,
        Movie.genres.any(lambda g: g.id in genre_ids)
    ).limit(limit).all()
    
    return similar


def get_cold_start_recommendations(db: Session, user_id: int, limit: int = 20) -> List[Movie]:
    """Get cold start recommendations"""
    return db.query(Movie).order_by(desc(Movie.rating), desc(Movie.view_count)).limit(limit).all()
''',

    "app/services/admin_service.py": '''"""Admin service"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.user import User
from app.models.movie import Movie
from app.models.watch_history import WatchHistory
from app.models.interaction import Interaction
from app.schemas.admin_schema import AdminStats, AdminUserResponse


def get_admin_stats(db: Session) -> AdminStats:
    """Get admin statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_movies = db.query(Movie).count()
    total_views = db.query(WatchHistory).count()
    total_interactions = db.query(Interaction).count()
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_movies=total_movies,
        total_views=total_views,
        total_interactions=total_interactions
    )


def get_all_users(db: Session) -> List[AdminUserResponse]:
    """Get all users with stats"""
    users = db.query(User).all()
    result = []
    
    for user in users:
        total_watch_time = db.query(func.sum(WatchHistory.watch_duration_seconds)).filter(
            WatchHistory.user_id == user.id
        ).scalar() or 0
        
        total_interactions = db.query(Interaction).filter(Interaction.user_id == user.id).count()
        
        result.append(AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            total_watch_time=total_watch_time,
            total_interactions=total_interactions
        ))
    
    return result
''',

    # AI/ML Files
    "app/ai/embeddings/minilm_model.py": '''"""MiniLM embedding model"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings

_model = None


def get_embedding_model():
    """Get or create embedding model"""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text"""
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str]) -> np.ndarray:
    """Generate embeddings for multiple texts"""
    model = get_embedding_model()
    embeddings = model.encode(texts)
    return embeddings
''',

    "app/ai/embeddings/build_movie_embeddings.py": '''"""Build movie embeddings"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.movie_embeddings import MovieEmbedding
from app.ai.embeddings.minilm_model import generate_embedding
from loguru import logger


def build_movie_embeddings():
    """Build embeddings for all movies"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        logger.info(f"Building embeddings for {len(movies)} movies")
        
        for movie in movies:
            # Create text representation
            text = f"{movie.title}. {movie.description or ''}. Genres: {', '.join([g.name for g in movie.genres])}"
            
            # Generate embedding
            embedding = generate_embedding(text)
            
            # Save or update
            movie_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == movie.id).first()
            if movie_emb:
                movie_emb.content_embedding = embedding
            else:
                movie_emb = MovieEmbedding(movie_id=movie.id, content_embedding=embedding)
                db.add(movie_emb)
            
            db.commit()
        
        logger.info("Movie embeddings built successfully")
    except Exception as e:
        logger.error(f"Error building movie embeddings: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    build_movie_embeddings()
''',

    "app/ai/embeddings/build_user_embeddings.py": '''"""Build user embeddings"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.user_features import UserFeatures
from app.models.interaction import Interaction
from app.models.movie_embeddings import MovieEmbedding
import numpy as np
from loguru import logger


def build_user_embedding(user_id: int, db: Session) -> list:
    """Build embedding for a user based on their interactions"""
    # Get user interactions
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    
    if not interactions:
        return None
    
    # Get movie embeddings for interacted movies
    movie_ids = [i.movie_id for i in interactions]
    movie_embeddings = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id.in_(movie_ids)).all()
    
    if not movie_embeddings:
        return None
    
    # Weighted average of movie embeddings
    embeddings = []
    weights = []
    
    for interaction in interactions:
        movie_emb = next((me for me in movie_embeddings if me.movie_id == interaction.movie_id), None)
        if movie_emb and movie_emb.content_embedding:
            embeddings.append(movie_emb.content_embedding)
            weights.append(interaction.interaction_value)
    
    if not embeddings:
        return None
    
    # Calculate weighted average
    embeddings_array = np.array(embeddings)
    weights_array = np.array(weights).reshape(-1, 1)
    user_embedding = np.average(embeddings_array, axis=0, weights=weights_array.flatten())
    
    return user_embedding.tolist()


def build_all_user_embeddings():
    """Build embeddings for all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Building embeddings for {len(users)} users")
        
        for user in users:
            embedding = build_user_embedding(user.id, db)
            if embedding:
                user_features = db.query(UserFeatures).filter(UserFeatures.user_id == user.id).first()
                if user_features:
                    user_features.user_embedding = embedding
                    db.commit()
        
        logger.info("User embeddings built successfully")
    except Exception as e:
        logger.error(f"Error building user embeddings: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    build_all_user_embeddings()
''',

    # Utilities
    "app/utils/helpers.py": '''"""Helper utilities"""
from typing import Any, Dict
import json


def serialize_json(data: Any) -> str:
    """Serialize data to JSON"""
    return json.dumps(data, default=str)


def deserialize_json(data: str) -> Dict:
    """Deserialize JSON to dict"""
    return json.loads(data)
''',

    "app/utils/validators.py": '''"""Validation utilities"""
import re


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password strength"""
    return len(password) >= 6
''',

    # README
    "README.md": '''# MEMAX OTT Platform

AI-Powered OTT Platform with Personalized Recommendations

## Features

- 🎬 Movie Streaming Platform
- 🤖 AI-Powered Recommendations
- 👤 User Authentication & Profiles
- 📊 Admin Dashboard
- 🔍 Advanced Search
- 📈 Analytics & Insights
- ⚡ Real-time Progress Tracking

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Sentence Transformers
- FAISS

### Frontend
- Next.js
- TypeScript
- TailwindCSS

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python -m app.db.init_db
python -m app.db.seed
python -m app.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Admin Credentials

- Email: admin@memax.com
- Password: admin123

**⚠️ Change these in production!**

## License

MIT
''',

    ".gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Database
*.db
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
.next/
dist/
build/

# AI Models
*.index
*.pkl
*.h5

# Data
app/data/raw/*
!app/data/raw/.gitkeep
app/data/processed/*
!app/data/processed/.gitkeep
'''
}


def create_file(path: str, content: str):
    """Create file with content"""
    file_path = BASE_DIR / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created: {path}")


def main():
    """Generate all files"""
    print("🚀 Generating MEMAX OTT Platform files...\n")
    
    for path, content in FILES.items():
        create_file(path, content)
    
    # Create empty __init__.py files
    init_dirs = [
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/routes",
        "app/services",
        "app/ai",
        "app/ai/embeddings",
        "app/ai/faiss",
        "app/ai/ranking",
        "app/ai/cold_start",
        "app/ai/baseline",
        "app/ai/orchestration",
        "app/ai/evaluation",
        "app/feature_store",
        "app/tasks",
        "app/cache",
        "app/utils",
        "app/admin_ui",
        "app/data",
        "app/data/raw",
        "app/data/processed",
        "app/data/loaders"
    ]
    
    for dir_path in init_dirs:
        create_file(f"{dir_path}/__init__.py", '"""Package initialization"""\\n')
    
    # Create placeholder files
    placeholders = [
        "app/data/raw/.gitkeep",
        "app/data/processed/.gitkeep",
        "app/ai/faiss/index_store/.gitkeep"
    ]
    
    for placeholder in placeholders:
        create_file(placeholder, "")
    
    print(f"\n✅ Generated {len(FILES) + len(init_dirs) + len(placeholders)} files successfully!")
    print("\n📝 Next steps:")
    print("1. cd backend")
    print("2. python -m venv venv")
    print("3. venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
    print("4. pip install -r requirements.txt")
    print("5. Copy .env.example to .env and configure")
    print("6. python setup_project.py")
    print("7. python -m app.main")


if __name__ == "__main__":
    main()
