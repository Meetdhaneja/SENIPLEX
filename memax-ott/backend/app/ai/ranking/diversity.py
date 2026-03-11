"""
Diversity Enhancement
Ensure diverse recommendations across genres, years, etc.
"""
import random
from typing import List, Tuple, Dict, Set
from collections import defaultdict
from loguru import logger
from sqlalchemy.orm import Session

from app.models.movie import Movie


class DiversityEnhancer:
    """Enhance diversity in recommendation lists"""
    
    def __init__(
        self,
        genre_diversity_weight: float = 0.3,
        year_diversity_weight: float = 0.2,
        country_diversity_weight: float = 0.1
    ):
        """
        Initialize diversity enhancer
        
        Args:
            genre_diversity_weight: Weight for genre diversity
            year_diversity_weight: Weight for year diversity
            country_diversity_weight: Weight for country diversity
        """
        self.genre_weight = genre_diversity_weight
        self.year_weight = year_diversity_weight
        self.country_weight = country_diversity_weight
    
    def diversify(
        self,
        recommendations: List[Tuple[int, float]],
        db: Session,
        target_size: int = None
    ) -> List[Tuple[int, float]]:
        """
        Rerank recommendations for diversity
        
        Args:
            recommendations: List of (movie_id, score) tuples
            db: Database session
            target_size: Target number of recommendations (default: same as input)
        
        Returns:
            Diversified list of (movie_id, score) tuples
        """
        if not recommendations:
            return []
        
        target_size = target_size or len(recommendations)
        
        try:
            # Get movie details
            movie_ids = [movie_id for movie_id, _ in recommendations]
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            movie_dict = {m.id: m for m in movies}
            
            # Track diversity
            selected = []
            remaining = list(recommendations)
            seen_genres = set()
            seen_decades = set()
            seen_countries = set()
            
            # Greedy selection with diversity
            while remaining and len(selected) < target_size:
                best_idx = 0
                best_score = -float('inf')
                
                for idx, (movie_id, score) in enumerate(remaining):
                    movie = movie_dict.get(movie_id)
                    if not movie:
                        continue
                    
                    # Calculate diversity bonus
                    diversity_bonus = self._calculate_diversity_bonus(
                        movie,
                        seen_genres,
                        seen_decades,
                        seen_countries
                    )
                    
                    # Combined score
                    combined_score = score + diversity_bonus
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_idx = idx
                
                # Add best item
                movie_id, score = remaining.pop(best_idx)
                selected.append((movie_id, score))
                
                # Update seen items
                movie = movie_dict.get(movie_id)
                if movie:
                    seen_genres.update(g.name for g in movie.genres)
                    if movie.release_year:
                        decade = (movie.release_year // 10) * 10
                        seen_decades.add(decade)
                    seen_countries.update(c.name for c in movie.countries)
            
            return selected
            
        except Exception as e:
            logger.error(f"Error in diversity enhancement: {str(e)}")
            return recommendations[:target_size]
    
    def _calculate_diversity_bonus(
        self,
        movie: Movie,
        seen_genres: Set[str],
        seen_decades: Set[int],
        seen_countries: Set[str]
    ) -> float:
        """Calculate diversity bonus for a movie"""
        bonus = 0.0
        
        # Genre diversity
        movie_genres = set(g.name for g in movie.genres)
        if movie_genres:
            genre_overlap = len(movie_genres & seen_genres) / len(movie_genres)
            genre_bonus = (1 - genre_overlap) * self.genre_weight
            bonus += genre_bonus
        
        # Year diversity
        if movie.release_year:
            decade = (movie.release_year // 10) * 10
            if decade not in seen_decades:
                bonus += self.year_weight
        
        # Country diversity
        movie_countries = set(c.name for c in movie.countries)
        if movie_countries:
            country_overlap = len(movie_countries & seen_countries) / len(movie_countries)
            country_bonus = (1 - country_overlap) * self.country_weight
            bonus += country_bonus
        
        return bonus
    
    def ensure_genre_coverage(
        self,
        recommendations: List[Tuple[int, float]],
        db: Session,
        min_genres: int = 3
    ) -> List[Tuple[int, float]]:
        """
        Ensure minimum genre coverage in recommendations
        
        Args:
            recommendations: List of (movie_id, score) tuples
            db: Database session
            min_genres: Minimum number of different genres
        
        Returns:
            Recommendations with genre coverage ensured
        """
        if not recommendations:
            return []
        
        try:
            # Get movie details
            movie_ids = [movie_id for movie_id, _ in recommendations]
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            movie_dict = {m.id: m for m in movies}
            
            # Group by genre
            genre_movies = defaultdict(list)
            for movie_id, score in recommendations:
                movie = movie_dict.get(movie_id)
                if movie:
                    for genre in movie.genres:
                        genre_movies[genre.name].append((movie_id, score))
            
            # Ensure coverage
            if len(genre_movies) < min_genres:
                # Already diverse enough
                return recommendations
            
            # Select from each genre
            result = []
            genres = list(genre_movies.keys())
            random.shuffle(genres)
            
            # Take at least one from each genre
            for genre in genres[:min_genres]:
                if genre_movies[genre]:
                    result.append(genre_movies[genre][0])
            
            # Fill remaining with top scores
            remaining = [
                item for item in recommendations
                if item not in result
            ]
            remaining.sort(key=lambda x: x[1], reverse=True)
            
            result.extend(remaining[:len(recommendations) - len(result)])
            
            return result
            
        except Exception as e:
            logger.error(f"Error ensuring genre coverage: {str(e)}")
            return recommendations


def apply_mmr_diversification(
    recommendations: List[Tuple[int, float]],
    similarity_matrix: Dict[Tuple[int, int], float],
    lambda_param: float = 0.5,
    target_size: int = None
) -> List[Tuple[int, float]]:
    """
    Apply Maximal Marginal Relevance (MMR) for diversification
    
    Args:
        recommendations: List of (movie_id, score) tuples
        similarity_matrix: Dict of (movie_id1, movie_id2) -> similarity
        lambda_param: Trade-off between relevance and diversity (0-1)
        target_size: Target number of recommendations
    
    Returns:
        Diversified recommendations
    """
    if not recommendations:
        return []
    
    target_size = target_size or len(recommendations)
    
    # Initialize
    selected = []
    remaining = list(recommendations)
    
    # Select first item (highest score)
    selected.append(remaining.pop(0))
    
    # Iteratively select items
    while remaining and len(selected) < target_size:
        best_idx = 0
        best_mmr = -float('inf')
        
        for idx, (movie_id, relevance) in enumerate(remaining):
            # Calculate max similarity to selected items
            max_sim = 0.0
            for selected_id, _ in selected:
                sim = similarity_matrix.get((movie_id, selected_id), 0.0)
                sim = max(sim, similarity_matrix.get((selected_id, movie_id), 0.0))
                max_sim = max(max_sim, sim)
            
            # MMR score
            mmr = lambda_param * relevance - (1 - lambda_param) * max_sim
            
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = idx
        
        # Add best item
        selected.append(remaining.pop(best_idx))
    
    return selected
