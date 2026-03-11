"""Recommendation log model"""
from sqlalchemy import Column, Integer, ForeignKey, JSON, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from datetime import datetime


class RecommendationLog(BaseModel):
    """Log of recommendations shown to users"""
    __tablename__ = "recommendation_logs"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, nullable=False)  # Not FK to allow deleted movies
    
    # Recommendation metadata
    recommendation_type = Column(String(100), nullable=False)  # personalized, trending, similar, etc.
    score = Column(Float, nullable=True)  # Recommendation score
    rank = Column(Integer, nullable=True)  # Position in recommendation list
    
    # Context
    context = Column(JSON, nullable=True)  # Additional context (page, filters, etc.)
    
    # Interaction tracking
    was_clicked = Column(Integer, default=0)  # 0 or 1
    was_watched = Column(Integer, default=0)  # 0 or 1
    watch_duration = Column(Integer, default=0)  # Seconds watched
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="recommendation_logs")
    
    def __repr__(self):
        return f"<RecommendationLog user={self.user_id} movie={self.movie_id} type={self.recommendation_type}>"
