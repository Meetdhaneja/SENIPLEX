from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.movie import Movie
from app.schemas.movies_schema import MovieCreate, MovieUpdate

class MovieService:

    @staticmethod
    async def get_all_movies(db: AsyncSession, limit: int = 50):
        result = await db.execute(select(Movie).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_movie_by_id(db: AsyncSession, movie_id: int):
        return await db.get(Movie, movie_id)

    @staticmethod
    async def create_movie(db: AsyncSession, data: MovieCreate):
        movie = Movie(
            title=data.title,
            description=data.description,
            release_year=data.release_year,
            duration_minutes=data.duration_minutes,
        )

        db.add(movie)
        await db.commit()
        await db.refresh(movie)
        return movie

    @staticmethod
    async def update_movie(
        db: AsyncSession,
        movie_id: int,
        data: MovieUpdate
    ):
        movie = await db.get(Movie, movie_id)
        if not movie:
            return None

        for field, value in data.dict(exclude_unset=True).items():
            setattr(movie, field, value)

        await db.commit()
        await db.refresh(movie)
        return movie
