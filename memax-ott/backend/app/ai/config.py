"""
AI Configuration Module
Central configuration for all AI/ML components
"""

import os
from pathlib import Path
from typing import Optional


class AIConfig:
    """Configuration for AI/ML components"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    INDEX_STORE_DIR = BASE_DIR / "faiss" / "index_store"
    MODEL_CACHE_DIR = BASE_DIR / "model_cache"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384  # MiniLM-L6-v2 output dimension
    MAX_SEQUENCE_LENGTH = 512
    
    # FAISS Configuration
    FAISS_INDEX_TYPE = "IndexFlatIP"  # Inner Product (cosine similarity)
    FAISS_NPROBE = 10  # Number of clusters to search
    FAISS_USE_GPU = False  # Set to True if GPU available
    
    # Movie Index
    MOVIE_INDEX_PATH = INDEX_STORE_DIR / "memax_movie.index"
    MOVIE_INDEX_METADATA_PATH = INDEX_STORE_DIR / "memax_movie_metadata.pkl"
    
    # User Index
    USER_INDEX_PATH = INDEX_STORE_DIR / "memax_user.index"
    USER_INDEX_METADATA_PATH = INDEX_STORE_DIR / "memax_user_metadata.pkl"
    
    # Recommendation Configuration
    TOP_K_CANDIDATES = 100  # Number of candidates from FAISS
    TOP_N_RECOMMENDATIONS = 20  # Final number of recommendations
    
    # Ranking Weights
    EMBEDDING_WEIGHT = 0.6
    POPULARITY_WEIGHT = 0.2
    RECENCY_WEIGHT = 0.2
    
    # Time Decay Configuration
    TIME_DECAY_FACTOR = 0.95  # Decay factor per day
    TIME_DECAY_MAX_DAYS = 365  # Maximum days to consider
    
    # Diversity Configuration
    DIVERSITY_LAMBDA = 0.5  # Balance between relevance and diversity
    MIN_GENRE_DIVERSITY = 0.3  # Minimum genre diversity in results
    
    # Cold Start Configuration
    NEW_USER_THRESHOLD_DAYS = 7  # Days to consider user as "new"
    NEW_MOVIE_THRESHOLD_DAYS = 30  # Days to consider movie as "new"
    MIN_USER_INTERACTIONS = 5  # Minimum interactions before personalization
    
    # Popularity Model
    POPULARITY_WINDOW_DAYS = 30  # Days to calculate popularity
    POPULARITY_MIN_VIEWS = 10  # Minimum views to be considered
    
    # Trending Model
    TRENDING_WINDOW_DAYS = 7  # Days to calculate trending
    TRENDING_GROWTH_WEIGHT = 0.7  # Weight for growth rate
    TRENDING_VOLUME_WEIGHT = 0.3  # Weight for absolute volume
    
    # Evaluation Metrics
    EVAL_TOP_K = [5, 10, 20]  # K values for precision@k, recall@k
    EVAL_MIN_TEST_USERS = 100  # Minimum users for evaluation
    
    # Batch Processing
    EMBEDDING_BATCH_SIZE = 32
    INDEX_BUILD_BATCH_SIZE = 1000
    RECOMMENDATION_BATCH_SIZE = 50
    
    # Cache Configuration
    CACHE_EMBEDDINGS = True
    CACHE_TTL_SECONDS = 3600  # 1 hour
    
    # Model Update Schedule
    REBUILD_INDEX_INTERVAL_HOURS = 24  # Rebuild FAISS index every 24 hours
    UPDATE_EMBEDDINGS_INTERVAL_HOURS = 6  # Update embeddings every 6 hours
    
    # Performance
    NUM_WORKERS = 4  # Number of parallel workers
    USE_MULTIPROCESSING = True
    
    # Logging
    LOG_RECOMMENDATIONS = True
    LOG_LEVEL = "INFO"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.INDEX_STORE_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: Optional[str] = None) -> Path:
        """
        Get path for cached model
        
        Args:
            model_name: Name of the model (defaults to EMBEDDING_MODEL_NAME)
            
        Returns:
            Path to model cache directory
        """
        model_name = model_name or cls.EMBEDDING_MODEL_NAME
        safe_name = model_name.replace("/", "_")
        return cls.MODEL_CACHE_DIR / safe_name
    
    @classmethod
    def get_index_path(cls, index_type: str = "movie") -> Path:
        """
        Get path for FAISS index
        
        Args:
            index_type: Type of index ("movie" or "user")
            
        Returns:
            Path to index file
        """
        if index_type == "movie":
            return cls.MOVIE_INDEX_PATH
        elif index_type == "user":
            return cls.USER_INDEX_PATH
        else:
            raise ValueError(f"Unknown index type: {index_type}")
    
    @classmethod
    def get_metadata_path(cls, index_type: str = "movie") -> Path:
        """
        Get path for index metadata
        
        Args:
            index_type: Type of index ("movie" or "user")
            
        Returns:
            Path to metadata file
        """
        if index_type == "movie":
            return cls.MOVIE_INDEX_METADATA_PATH
        elif index_type == "user":
            return cls.USER_INDEX_METADATA_PATH
        else:
            raise ValueError(f"Unknown index type: {index_type}")


# Environment-based overrides
if os.getenv("AI_USE_GPU", "false").lower() == "true":
    AIConfig.FAISS_USE_GPU = True

if os.getenv("AI_EMBEDDING_MODEL"):
    AIConfig.EMBEDDING_MODEL_NAME = os.getenv("AI_EMBEDDING_MODEL")

if os.getenv("AI_TOP_N"):
    AIConfig.TOP_N_RECOMMENDATIONS = int(os.getenv("AI_TOP_N"))

# Ensure directories exist
AIConfig.ensure_directories()


# Export commonly used values
EMBEDDING_DIM = AIConfig.EMBEDDING_DIMENSION
TOP_K = AIConfig.TOP_K_CANDIDATES
TOP_N = AIConfig.TOP_N_RECOMMENDATIONS
MODEL_NAME = AIConfig.EMBEDDING_MODEL_NAME
