"""
Hybrid Ranking System
Combines multiple signals for better recommendations
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.interaction import Interaction
from app.models.watch_history import WatchHistory


class HybridRanker:
    """Hybrid ranking combining multiple signals"""
    
    def __init__(
        self,
        content_weight: float = 0.4,
        collaborative_weight: float = 0.3,
        popularity_weight: float = 0.2,
        recency_weight: float = 0.1
    ):
        """
        Initialize hybrid ranker with weights
        
        Args:
            content_weight: Weight for content-based similarity
            collaborative_weight: Weight for collaborative filtering
            popularity_weight: Weight for popularity score
            recency_weight: Weight for recency score
        """
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        self.popularity_weight = popularity_weight
        self.recency_weight = recency_weight
        
        # Normalize weights
        total = sum([content_weight, collaborative_weight, popularity_weight, recency_weight])
        self.content_weight /= total
        self.collaborative_weight /= total
        self.popularity_weight /= total
        self.recency_weight /= total
    
    def rank(
        self,
        candidates: List[Tuple[int, float]],
        user_id: int,
        db: Session,
        collaborative_scores: Optional[Dict[int, float]] = None,
        diversity_boost: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Rank candidate movies using hybrid approach with country-wise consideration
        
        Args:
            candidates: List of (movie_id, content_similarity) tuples
            user_id: User ID for personalization
            db: Database session
            collaborative_scores: Optional collaborative filtering scores
            diversity_boost: Whether to boost diversity
        
        Returns:
            Ranked list of (movie_id, final_score) tuples
        """
        if not candidates:
            return []
        
        try:
            movie_ids = [movie_id for movie_id, _ in candidates]
            
            # Get movies from database
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            movie_dict = {m.id: m for m in movies}
            
            # Identify user country preferences based on past interactions
            user_preferred_countries = set()
            recent_interactions = db.query(Interaction).filter(
                Interaction.user_id == user_id
            ).order_by(Interaction.timestamp.desc()).limit(20).all()
            
            for interaction in recent_interactions:
                imovie = db.query(Movie).filter(Movie.id == interaction.movie_id).first()
                if imovie and imovie.countries:
                    for c in imovie.countries:
                        user_preferred_countries.add(c.name)
            
            # Calculate different scores
            content_scores = {movie_id: score for movie_id, score in candidates}
            popularity_scores = self._calculate_popularity_scores(movies)
            recency_scores = self._calculate_recency_scores(movies)
            
            # Combine scores
            final_scores = []
            for movie_id in movie_ids:
                if movie_id not in movie_dict:
                    continue
                
                # Content similarity score
                content_score = content_scores.get(movie_id, 0.0)
                
                # Collaborative score
                collab_score = 0.0
                if collaborative_scores and movie_id in collaborative_scores:
                    collab_score = collaborative_scores[movie_id]
                
                # Popularity score
                pop_score = popularity_scores.get(movie_id, 0.0)
                
                # Recency score
                rec_score = recency_scores.get(movie_id, 0.0)
                
                # Weighted combination
                final_score = (
                    self.content_weight * content_score +
                    self.collaborative_weight * collab_score +
                    self.popularity_weight * pop_score +
                    self.recency_weight * rec_score
                )
                
                # Apply country-wise affinity boost
                movie = movie_dict[movie_id]
                movie_countries = [c.name for c in movie.countries] if movie.countries else []
                if user_preferred_countries and any(c in user_preferred_countries for c in movie_countries):
                    # Boost score by 20% if country matches user history
                    final_score *= 1.2
                
                final_scores.append((movie_id, final_score))
            
            # Sort by final score
            final_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Apply diversity boost if requested
            if diversity_boost:
                final_scores = self._apply_diversity_boost(final_scores, movie_dict)
            
            return final_scores
            
        except Exception as e:
            logger.error(f"Error in hybrid ranking: {str(e)}")
            return candidates
    
    def _calculate_popularity_scores(self, movies: List[Movie]) -> Dict[int, float]:
        """Calculate popularity scores based on view count and rating"""
        scores = {}
        
        if not movies:
            return scores
        
        # Get max values for normalization
        max_views = max(m.view_count for m in movies) or 1
        max_rating = 10.0
        
        for movie in movies:
            # Combine view count and rating
            view_score = movie.view_count / max_views
            rating_score = (movie.rating or 0) / max_rating
            
            # Weighted combination
            scores[movie.id] = 0.6 * view_score + 0.4 * rating_score
        
        return scores
    
    def _calculate_recency_scores(self, movies: List[Movie]) -> Dict[int, float]:
        """Calculate recency scores based on release year"""
        scores = {}
        current_year = datetime.now().year
        
        for movie in movies:
            if movie.release_year:
                # More recent movies get higher scores
                years_old = current_year - movie.release_year
                # Decay over 20 years
                score = max(0, 1 - (years_old / 20))
                scores[movie.id] = score
            else:
                scores[movie.id] = 0.5  # Default for unknown year
        
        return scores
    
    def _apply_diversity_boost(
        self,
        ranked_movies: List[Tuple[int, float]],
        movie_dict: Dict[int, Movie]
    ) -> List[Tuple[int, float]]:
        """Apply diversity boost to avoid too similar recommendations"""
        if len(ranked_movies) <= 1:
            return ranked_movies
        
        try:
            diversified = []
            seen_genres = set()
            seen_years = set()
            
            # First pass: take top items with diversity
            for movie_id, score in ranked_movies:
                movie = movie_dict.get(movie_id)
                if not movie:
                    continue
                
                # Get movie genres
                movie_genres = set(g.name for g in movie.genres)
                movie_decade = (movie.release_year // 10) * 10 if movie.release_year else None
                
                # Calculate diversity penalty
                genre_overlap = len(movie_genres & seen_genres)
                diversity_penalty = genre_overlap * 0.05
                
                # Apply penalty
                adjusted_score = score * (1 - diversity_penalty)
                
                diversified.append((movie_id, adjusted_score))
                
                # Update seen items
                seen_genres.update(movie_genres)
                if movie_decade:
                    seen_years.add(movie_decade)
            
            # Re-sort by adjusted scores
            diversified.sort(key=lambda x: x[1], reverse=True)
            
            return diversified
            
        except Exception as e:
            logger.error(f"Error applying diversity boost: {str(e)}")
            return ranked_movies


def create_hybrid_ranker(profile: str = "balanced") -> HybridRanker:
    """
    Create hybrid ranker with predefined profile
    
    Args:
        profile: One of 'balanced', 'content', 'collaborative', 'popular', 'fresh'
    
    Returns:
        Configured HybridRanker instance
    """
    profiles = {
        'balanced': (0.4, 0.3, 0.2, 0.1),
        'content': (0.7, 0.2, 0.05, 0.05),
        'collaborative': (0.2, 0.6, 0.1, 0.1),
        'popular': (0.2, 0.2, 0.5, 0.1),
        'fresh': (0.3, 0.2, 0.1, 0.4)
    }
    
    weights = profiles.get(profile, profiles['balanced'])
    return HybridRanker(*weights)
