"""Watch progress model"""
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from datetime import datetime


class WatchProgress(BaseModel):
    """Watch progress database model"""
    __tablename__ = "watch_progress"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    progress_seconds = Column(Integer, default=0, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    last_watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="watch_progress")
    movie = relationship("Movie", back_populates="watch_progress")
    
    def __repr__(self):
        return f"<WatchProgress user={self.user_id} movie={self.movie_id} progress={self.progress_percentage}%>"
