"""Movie embeddings model"""
from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import BaseModel


class MovieEmbedding(BaseModel):
    """Movie embeddings for similarity search"""
    __tablename__ = "movie_embeddings"
    
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Embeddings
    content_embedding = Column(JSON, nullable=True)  # Based on title, description, genres
    collaborative_embedding = Column(JSON, nullable=True)  # Based on user interactions
    
    # Metadata for indexing
    faiss_index_id = Column(Integer, nullable=True)  # Position in FAISS index
    
    # Relationships
    movie = relationship("Movie", back_populates="embeddings")
    
    def __repr__(self):
        return f"<MovieEmbedding movie_id={self.movie_id}>"
