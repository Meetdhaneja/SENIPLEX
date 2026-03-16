"""
Recommendation Service - AI-Powered
Integrates with the AI recommendation pipeline for advanced ML-based recommendations
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from loguru import logger

from app.models.movie import Movie
from app.models.interaction import Interaction
from app.schemas.recommendation_schema import (
    RecommendationRequest, 
    RecommendationResponse, 
    RecommendationItem
)
from app.schemas.movie_schema import MovieResponse

# Import AI pipeline
from app.ai.orchestration.recommendation_pipeline import get_pipeline


class RecommendationService:
    """AI-powered recommendation service"""
    
    def __init__(self):
        """Initialize recommendation service with AI pipeline"""
        self.pipeline = get_pipeline(
            ranking_profile='balanced',
            enable_diversity=True
        )
    
    def get_personalized_recommendations(
        self,
        db: Session,
        user_id: int,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Get AI-powered personalized recommendations for user
        
        Args:
            db: Database session
            user_id: User ID
            request: Recommendation request parameters
            
        Returns:
            RecommendationResponse with personalized recommendations
        """
        try:
            # Get movie IDs from AI pipeline
            movie_ids = self.pipeline.get_recommendations(
                user_id=user_id,
                db=db,
                count=request.limit,
                exclude_watched=request.exclude_watched
            )
            
            if not movie_ids:
                logger.warning(f"No recommendations found for user {user_id}, using fallback")
                return self._fallback_recommendations(db, request)
            
            # Fetch movie details
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            
            # Create movie ID to movie mapping for ordering
            movie_map = {movie.id: movie for movie in movies}
            
            # Build recommendations in the order returned by AI
            recommendations = []
            for idx, movie_id in enumerate(movie_ids):
                movie = movie_map.get(movie_id)
                if movie:
                    # Calculate score (higher for earlier recommendations)
                    score = 1.0 - (idx * 0.05)
                    score = max(0.5, min(1.0, score))
                    
                    # Use safe serialization from movie_service to prevent lazy-load crashes
                    from app.services.movie_service import _safe_serialize
                    movie_dict = _safe_serialize(movie)
                    
                    if movie_dict:
                        recommendations.append(
                            RecommendationItem(
                                movie=movie_dict,
                                score=score,
                                reason=reason
                            )
                        )
            
            logger.info(f"Generated {len(recommendations)} AI recommendations for user {user_id}")
            
            return RecommendationResponse(
                recommendations=recommendations,
                recommendation_type="ai_personalized"
            )
            
        except Exception as e:
            logger.error(f"Error in AI recommendations for user {user_id}: {str(e)}")
            return self._fallback_recommendations(db, request)
    
    def get_similar_movies(
        self,
        db: Session,
        movie_id: int,
        limit: int = 10
    ) -> List[Movie]:
        """
        Get AI-powered similar movies
        
        Args:
            db: Database session
            movie_id: Movie ID to find similar movies for
            limit: Number of similar movies to return
            
        Returns:
            List of similar Movie objects
        """
        try:
            # Get similar movie IDs from AI pipeline
            similar_ids = self.pipeline.get_similar_movies(
                movie_id=movie_id,
                db=db,
                count=limit
            )
            
            if not similar_ids:
                logger.warning(f"No similar movies found for movie {movie_id}, using fallback")
                return self._fallback_similar_movies(db, movie_id, limit)
            
            # Fetch and return movies in order
            movies = db.query(Movie).filter(Movie.id.in_(similar_ids)).all()
            movie_map = {movie.id: movie for movie in movies}
            
            # Return in the order provided by AI
            ordered_movies = [movie_map[mid] for mid in similar_ids if mid in movie_map]
            
            logger.info(f"Found {len(ordered_movies)} similar movies for movie {movie_id}")
            return ordered_movies
            
        except Exception as e:
            logger.error(f"Error getting similar movies for {movie_id}: {str(e)}")
            return self._fallback_similar_movies(db, movie_id, limit)
    
    def get_cold_start_recommendations(
        self,
        db: Session,
        user_id: int,
        limit: int = 20
    ) -> List[Movie]:
        """
        Get cold start recommendations for new users
        
        Args:
            db: Database session
            user_id: User ID
            limit: Number of recommendations
            
        Returns:
            List of Movie objects
        """
        try:
            # Use AI pipeline's cold start logic
            movie_ids = self.pipeline._cold_start_recommendations(
                user_id=user_id,
                db=db,
                count=limit
            )
            
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            logger.info(f"Generated {len(movies)} cold start recommendations for user {user_id}")
            return movies
            
        except Exception as e:
            logger.error(f"Error in cold start recommendations: {str(e)}")
            return self._fallback_cold_start(db, limit)
    
    def get_trending_recommendations(
        self,
        db: Session,
        limit: int = 20,
        content_type: Optional[str] = None
    ) -> List[Movie]:
        """
        Get trending movies
        
        Args:
            db: Database session
            limit: Number of trending movies
            content_type: Optional content type filter
            
        Returns:
            List of trending Movie objects
        """
        try:
            movie_ids = self.pipeline.get_trending_recommendations(
                db=db,
                count=limit,
                content_type=content_type
            )
            
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            movie_map = {movie.id: movie for movie in movies}
            
            # Return in trending order
            ordered_movies = [movie_map[mid] for mid in movie_ids if mid in movie_map]
            
            logger.info(f"Found {len(ordered_movies)} trending movies")
            return ordered_movies
            
        except Exception as e:
            logger.error(f"Error getting trending movies: {str(e)}")
            return []
    
    def get_popular_recommendations(
        self,
        db: Session,
        limit: int = 20,
        genre_filter: Optional[List[str]] = None
    ) -> List[Movie]:
        """
        Get popular movies
        
        Args:
            db: Database session
            limit: Number of popular movies
            genre_filter: Optional genre filter
            
        Returns:
            List of popular Movie objects
        """
        try:
            movie_ids = self.pipeline.get_popular_recommendations(
                db=db,
                count=limit,
                genre_filter=genre_filter
            )
            
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            movie_map = {movie.id: movie for movie in movies}
            
            # Return in popularity order
            ordered_movies = [movie_map[mid] for mid in movie_ids if mid in movie_map]
            
            logger.info(f"Found {len(ordered_movies)} popular movies")
            return ordered_movies
            
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []
    
    def _generate_reason(self, user_id: int, movie: Movie, db: Session) -> str:
        """Generate recommendation reason"""
        # Check if user is new
        interaction_count = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).count()
        
        if interaction_count < 5:
            return "Popular among viewers like you"
        
        # Get user's genre preferences from interactions
        user_genres = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).join(Movie).join(Movie.genres).limit(10).all()
        
        if user_genres:
            return "Based on your viewing history"
        
        return "Recommended for you"
    
    def _fallback_recommendations(
        self,
        db: Session,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """Fallback to simple rating-based recommendations"""
        from sqlalchemy import desc
        
        movies = db.query(Movie).order_by(
            desc(Movie.rating),
            desc(Movie.view_count)
        ).limit(request.limit).all()
        
        from app.services.movie_service import _safe_serialize
        
        recommendations = []
        for movie in movies:
            serialized = _safe_serialize(movie)
            if serialized:
                recommendations.append(
                    RecommendationItem(
                        movie=serialized,
                        score=movie.rating / 10.0 if hasattr(movie, 'rating') else 0.8,
                        reason="Highly rated"
                    )
                )
        
        return RecommendationResponse(
            recommendations=recommendations,
            recommendation_type="fallback_rating"
        )
    
    def _fallback_similar_movies(
        self,
        db: Session,
        movie_id: int,
        limit: int
    ) -> List[Movie]:
        """Fallback to genre-based similar movies"""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie or not movie.genres:
            return []
        
        genre_ids = [g.id for g in movie.genres]
        
        similar = db.query(Movie).join(Movie.genres).filter(
            Movie.id != movie_id,
            Movie.genres.any(lambda g: g.id in genre_ids)
        ).limit(limit).all()
        
        return similar
    
    def _fallback_cold_start(self, db: Session, limit: int) -> List[Movie]:
        """Fallback cold start recommendations"""
        from sqlalchemy import desc
        
        return db.query(Movie).order_by(
            desc(Movie.rating),
            desc(Movie.view_count)
        ).limit(limit).all()


# Global service instance
_service_instance: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    """Get or create global recommendation service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = RecommendationService()
    return _service_instance


# Convenience functions for backward compatibility
def get_personalized_recommendations(
    db: Session,
    user_id: int,
    request: RecommendationRequest
) -> RecommendationResponse:
    """Get personalized recommendations (convenience function)"""
    service = get_recommendation_service()
    return service.get_personalized_recommendations(db, user_id, request)


def get_similar_movies(db: Session, movie_id: int, limit: int = 10) -> List[Movie]:
    """Get similar movies (convenience function)"""
    service = get_recommendation_service()
    return service.get_similar_movies(db, movie_id, limit)


def get_cold_start_recommendations(db: Session, user_id: int, limit: int = 20) -> List[Movie]:
    """Get cold start recommendations (convenience function)"""
    service = get_recommendation_service()
    return service.get_cold_start_recommendations(db, user_id, limit)
