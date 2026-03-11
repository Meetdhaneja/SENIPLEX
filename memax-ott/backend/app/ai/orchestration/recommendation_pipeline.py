"""
Recommendation Pipeline Orchestration
Coordinates all recommendation components
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger
import numpy as np

from app.ai.faiss.search import get_search_instance
from app.ai.ranking.hybrid_ranker import create_hybrid_ranker
from app.ai.ranking.diversity import DiversityEnhancer
from app.ai.cold_start.new_user import NewUserRecommender
from app.ai.baseline.popularity_model import PopularityModel
from app.ai.baseline.trending_model import TrendingModel
from app.models.user_embeddings import UserEmbedding
from app.models.interaction import Interaction
from app.models.watch_history import WatchHistory


class RecommendationPipeline:
    """End-to-end recommendation pipeline"""
    
    def __init__(
        self,
        ranking_profile: str = 'balanced',
        enable_diversity: bool = True,
        enable_cold_start: bool = True
    ):
        """
        Initialize recommendation pipeline
        
        Args:
            ranking_profile: Ranking profile ('balanced', 'content', 'collaborative', 'popular', 'fresh')
            enable_diversity: Whether to apply diversity enhancement
            enable_cold_start: Whether to use cold start strategies
        """
        self.ranking_profile = ranking_profile
        self.enable_diversity = enable_diversity
        self.enable_cold_start = enable_cold_start
        
        # Initialize components
        self.faiss_search = get_search_instance()
        self.hybrid_ranker = create_hybrid_ranker(ranking_profile)
        self.diversity_enhancer = DiversityEnhancer()
        self.new_user_recommender = NewUserRecommender()
        self.popularity_model = PopularityModel()
        self.trending_model = TrendingModel()
    
    def get_recommendations(
        self,
        user_id: int,
        db: Session,
        count: int = 20,
        exclude_watched: bool = True,
        context: Optional[Dict] = None
    ) -> List[int]:
        """
        Get personalized recommendations for user
        
        Args:
            user_id: User ID
            db: Database session
            count: Number of recommendations
            exclude_watched: Whether to exclude already watched movies
            context: Optional context dict (time_of_day, device, etc.)
        
        Returns:
            List of recommended movie IDs
        """
        try:
            # Check if new user (cold start)
            if self.enable_cold_start and self._is_new_user(user_id, db):
                logger.info(f"Using cold start for new user {user_id}")
                return self._cold_start_recommendations(user_id, db, count)
            
            # Get user embedding
            user_embedding_data = db.query(UserEmbedding).filter(
                UserEmbedding.user_id == user_id
            ).first()
            
            if not user_embedding_data or not user_embedding_data.preference_embedding:
                logger.warning(f"No embedding for user {user_id}, using cold start")
                return self._cold_start_recommendations(user_id, db, count)
            
            # Convert embedding
            user_embedding = np.frombuffer(
                user_embedding_data.preference_embedding,
                dtype=np.float32
            )
            
            # Get watched movies to exclude
            exclude_ids = []
            if exclude_watched:
                exclude_ids = self._get_watched_movies(user_id, db)
            
            # Search for candidate movies
            candidates = self.faiss_search.search_similar(
                user_embedding,
                k=count * 3,  # Get extra for filtering and ranking
                exclude_ids=exclude_ids
            )
            
            if not candidates:
                logger.warning(f"No candidates found for user {user_id}")
                return self._fallback_recommendations(db, count)
            
            # Rank candidates with hybrid approach
            ranked = self.hybrid_ranker.rank(
                candidates=candidates,
                user_id=user_id,
                db=db,
                diversity_boost=self.enable_diversity
            )
            
            # Apply diversity enhancement
            if self.enable_diversity and len(ranked) > count:
                ranked = self.diversity_enhancer.diversify(
                    ranked,
                    db,
                    target_size=count
                )
            
            # Extract movie IDs
            recommendations = [movie_id for movie_id, _ in ranked[:count]]
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in recommendation pipeline: {str(e)}")
            return self._fallback_recommendations(db, count)
    
    def get_similar_movies(
        self,
        movie_id: int,
        db: Session,
        count: int = 10
    ) -> List[int]:
        """
        Get movies similar to given movie
        
        Args:
            movie_id: Movie ID
            db: Database session
            count: Number of similar movies
        
        Returns:
            List of similar movie IDs
        """
        try:
            similar = self.faiss_search.get_movie_neighbors(movie_id, k=count)
            return [mid for mid, _ in similar]
        except Exception as e:
            logger.error(f"Error getting similar movies: {str(e)}")
            return []
    
    def get_trending_recommendations(
        self,
        db: Session,
        count: int = 20,
        content_type: Optional[str] = None
    ) -> List[int]:
        """Get trending movies"""
        try:
            trending = self.trending_model.get_trending_movies(
                db,
                count=count,
                content_type=content_type
            )
            return [movie_id for movie_id, _ in trending]
        except Exception as e:
            logger.error(f"Error getting trending: {str(e)}")
            return []
    
    def get_popular_recommendations(
        self,
        db: Session,
        count: int = 20,
        genre_filter: Optional[List[str]] = None
    ) -> List[int]:
        """Get popular movies"""
        try:
            popular = self.popularity_model.get_popular_movies(
                db,
                count=count,
                genre_filter=genre_filter
            )
            return [movie_id for movie_id, _ in popular]
        except Exception as e:
            logger.error(f"Error getting popular: {str(e)}")
            return []
    
    def _is_new_user(self, user_id: int, db: Session) -> bool:
        """Check if user is new (has few interactions)"""
        interaction_count = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).count()
        return interaction_count < 5
    
    def _get_watched_movies(self, user_id: int, db: Session) -> List[int]:
        """Get list of movies user has watched"""
        watched = db.query(WatchHistory.movie_id).filter(
            WatchHistory.user_id == user_id
        ).distinct().all()
        return [movie_id for movie_id, in watched]
    
    def _cold_start_recommendations(
        self,
        user_id: int,
        db: Session,
        count: int
    ) -> List[int]:
        """Get recommendations for new user"""
        return self.new_user_recommender.get_recommendations(db, count=count)
    
    def _fallback_recommendations(self, db: Session, count: int) -> List[int]:
        """Fallback recommendations when pipeline fails"""
        return self.get_popular_recommendations(db, count)


# Global pipeline instance
_pipeline_instance: Optional[RecommendationPipeline] = None


def get_pipeline(
    ranking_profile: str = 'balanced',
    enable_diversity: bool = True
) -> RecommendationPipeline:
    """Get or create global pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RecommendationPipeline(
            ranking_profile=ranking_profile,
            enable_diversity=enable_diversity
        )
    return _pipeline_instance


def get_user_recommendations(
    user_id: int,
    db: Session,
    count: int = 20
) -> List[int]:
    """Convenience function to get user recommendations"""
    pipeline = get_pipeline()
    return pipeline.get_recommendations(user_id, db, count)
