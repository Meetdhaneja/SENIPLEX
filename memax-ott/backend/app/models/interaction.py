"""Interaction model"""
from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from datetime import datetime


class Interaction(BaseModel):
    """User-Movie interaction database model"""
    __tablename__ = "interactions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # view, like, dislike, search, click
    rating = Column(Float, nullable=True)  # User rating if applicable
    interaction_value = Column(Float, default=1.0)  # Weight of interaction
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    movie = relationship("Movie", back_populates="interactions")
    
    def __repr__(self):
        return f"<Interaction user={self.user_id} movie={self.movie_id} type={self.interaction_type}>"
