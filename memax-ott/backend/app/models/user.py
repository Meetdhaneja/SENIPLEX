"""User model"""
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.base import BaseModel


class User(BaseModel):
    """User database model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    profile_picture = Column(String(500), nullable=True)
    
    # Relationships
    watch_history = relationship("WatchHistory", back_populates="user", cascade="all, delete-orphan")
    watch_progress = relationship("WatchProgress", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    user_features = relationship("UserFeatures", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recommendation_logs = relationship("RecommendationLog", back_populates="user", cascade="all, delete-orphan")
    embedding = relationship("UserEmbedding", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"
