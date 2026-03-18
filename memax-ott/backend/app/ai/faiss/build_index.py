"""
FAISS Index Builder
Builds and manages FAISS index for fast similarity search
"""
import faiss
import numpy as np
from pathlib import Path
from typing import Any, List, Optional, cast
from loguru import logger
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.movie_embeddings import MovieEmbedding
from app.models.movie import Movie


class FAISSIndexBuilder:
    """Build and manage FAISS index for movie embeddings"""
    
    def __init__(self, index_path: str = "app/ai/faiss/index_store/memax_movie.index"):
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index: Optional[faiss.Index] = None
        self.movie_ids: List[int] = []
        self.dimension = 384  # MiniLM embedding dimension
    
    def build_index(self, db: Session | None = None) -> bool:
        """Build FAISS index from database embeddings"""
        owns_session = db is None
        db = SessionLocal() if db is None else db
        
        try:
            logger.info("Building FAISS index...")
            
            # Fetch all movie embeddings
            # `MovieEmbedding.content_embedding` is declared as a Python value type in the model
            # for assignment convenience, which confuses static typing for SQLAlchemy expressions.
            # Casting to `Any` keeps runtime behavior identical while satisfying type checking.
            me = cast(Any, MovieEmbedding)
            m = cast(Any, Movie)
            embeddings_data = db.query(me.movie_id, me.content_embedding).join(m).filter(
                m.is_active == True,
                me.content_embedding.isnot(None),
            ).all()
            
            if not embeddings_data:
                logger.warning("No embeddings found in database")
                return False
            
            # Extract embeddings and movie IDs
            self.movie_ids = [item.movie_id for item in embeddings_data]
            embeddings = np.array([
                np.array(item.content_embedding, dtype=np.float32)
                for item in embeddings_data
            ])
            
            logger.info(f"Loaded {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")
            
            # Create FAISS index
            # Using IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            # faiss' runtime binding accepts `add(x)` but type stubs may expect other signatures.
            cast(Any, self.index).add(embeddings)
            
            logger.info(f"FAISS index built with {self.index.ntotal} vectors")
            
            # Save index
            self.save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {str(e)}")
            return False
        finally:
            if owns_session:
                db.close()
    
    def save_index(self) -> bool:
        """Save FAISS index to disk"""
        try:
            if self.index is None:
                logger.error("No index to save")
                return False
            
            # Save index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save movie IDs mapping
            movie_ids_path = self.index_path.with_suffix('.npy')
            np.save(movie_ids_path, np.array(self.movie_ids))
            
            logger.info(f"FAISS index saved to {self.index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            return False
    
    def load_index(self) -> bool:
        """Load FAISS index from disk"""
        try:
            if not self.index_path.exists():
                logger.warning(f"Index file not found: {self.index_path}")
                return False
            
            # Load index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load movie IDs mapping
            movie_ids_path = self.index_path.with_suffix('.npy')
            if movie_ids_path.exists():
                self.movie_ids = np.load(movie_ids_path).tolist()
            
            assert self.index is not None
            logger.info(f"FAISS index loaded with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            return False
    
    def add_movie_embedding(self, movie_id: int, embedding: np.ndarray) -> bool:
        """Add single movie embedding to index"""
        try:
            if self.index is None:
                logger.error("Index not initialized")
                return False
            
            # Normalize embedding
            embedding = embedding.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(embedding)
            
            # Add to index
            cast(Any, self.index).add(embedding)
            self.movie_ids.append(movie_id)
            
            # Save updated index
            self.save_index()
            
            logger.info(f"Added movie {movie_id} to FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Error adding movie to index: {str(e)}")
            return False
    
    def rebuild_index(self) -> bool:
        """Rebuild index from scratch"""
        logger.info("Rebuilding FAISS index from scratch...")
        return self.build_index()


def build_faiss_index():
    """Standalone function to build FAISS index"""
    builder = FAISSIndexBuilder()
    return builder.build_index()


if __name__ == "__main__":
    build_faiss_index()
