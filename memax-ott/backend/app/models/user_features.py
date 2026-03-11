"""User features model for ML"""
from sqlalchemy import Column, Integer, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.db.base import BaseModel


class UserFeatures(BaseModel):
    """User features for recommendation engine"""
    __tablename__ = "user_features"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Preference features
    favorite_genres = Column(JSON, nullable=True)  # List of genre IDs with weights
    favorite_actors = Column(JSON, nullable=True)  # List of actors with weights
    favorite_directors = Column(JSON, nullable=True)  # List of directors with weights
    
    # Behavioral features
    avg_watch_duration = Column(Float, default=0.0)
    total_watch_time = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    
    # Embedding
    user_embedding = Column(JSON, nullable=True)  # Vector representation
    
    # Relationships
    user = relationship("User", back_populates="user_features")
    
    def __repr__(self):
        return f"<UserFeatures user_id={self.user_id}>"
