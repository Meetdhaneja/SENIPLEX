"""Genre model"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.movie import movie_genres


class Genre(BaseModel):
    """Genre database model"""
    __tablename__ = "genres"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    
    # Relationships
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")
    
    def __repr__(self):
        return f"<Genre {self.name}>"
