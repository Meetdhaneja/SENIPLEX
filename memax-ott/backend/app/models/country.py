"""Country model"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.movie import movie_countries


class Country(BaseModel):
    """Country database model"""
    __tablename__ = "countries"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(10), nullable=True)  # ISO country code
    
    # Relationships
    movies = relationship("Movie", secondary=movie_countries, back_populates="countries")
    
    def __repr__(self):
        return f"<Country {self.name}>"
