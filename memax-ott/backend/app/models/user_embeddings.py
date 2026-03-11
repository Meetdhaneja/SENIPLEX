"""User Embeddings model"""
from sqlalchemy import Column, Integer, ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from datetime import datetime


class UserEmbedding(BaseModel):
    """User embedding database model"""
    __tablename__ = "user_embeddings"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    preference_embedding = Column(LargeBinary, nullable=True)  # Numpy array as bytes
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="embedding")
    
    def __repr__(self):
        return f"<UserEmbedding user_id={self.user_id}>"
