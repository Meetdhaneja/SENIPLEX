"""Watch history model"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from datetime import datetime


class WatchHistory(BaseModel):
    """Watch history database model"""
    __tablename__ = "watch_history"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed = Column(Boolean, default=False)
    watch_duration_seconds = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="watch_history")
    movie = relationship("Movie", back_populates="watch_history")
    
    def __repr__(self):
        return f"<WatchHistory user={self.user_id} movie={self.movie_id}>"
