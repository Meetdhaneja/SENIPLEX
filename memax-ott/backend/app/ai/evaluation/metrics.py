"""
Recommendation Evaluation Metrics
Measure recommendation quality
"""
from typing import List, Dict, Set
import numpy as np
from loguru import logger


class RecommendationMetrics:
    """Calculate recommendation quality metrics"""
    
    @staticmethod
    def precision_at_k(
        recommended: List[int],
        relevant: Set[int],
        k: int = 10
    ) -> float:
        """
        Calculate Precision@K
        
        Args:
            recommended: List of recommended item IDs
            relevant: Set of relevant item IDs
            k: Number of top items to consider
        
        Returns:
            Precision@K score
        """
        if not recommended or not relevant:
            return 0.0
        
        top_k = recommended[:k]
        relevant_in_top_k = sum(1 for item in top_k if item in relevant)
        
        return relevant_in_top_k / k
    
    @staticmethod
    def recall_at_k(
        recommended: List[int],
        relevant: Set[int],
        k: int = 10
    ) -> float:
        """
        Calculate Recall@K
        
        Args:
            recommended: List of recommended item IDs
            relevant: Set of relevant item IDs
            k: Number of top items to consider
        
        Returns:
            Recall@K score
        """
        if not recommended or not relevant:
            return 0.0
        
        top_k = recommended[:k]
        relevant_in_top_k = sum(1 for item in top_k if item in relevant)
        
        return relevant_in_top_k / len(relevant)
    
    @staticmethod
    def ndcg_at_k(
        recommended: List[int],
        relevant: Dict[int, float],
        k: int = 10
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain@K
        
        Args:
            recommended: List of recommended item IDs
            relevant: Dict mapping item ID to relevance score
            k: Number of top items to consider
        
        Returns:
            NDCG@K score
        """
        if not recommended or not relevant:
            return 0.0
        
        # Calculate DCG
        dcg = 0.0
        for i, item_id in enumerate(recommended[:k]):
            if item_id in relevant:
                relevance = relevant[item_id]
                dcg += relevance / np.log2(i + 2)  # i+2 because i is 0-indexed
        
        # Calculate IDCG (ideal DCG)
        ideal_relevances = sorted(relevant.values(), reverse=True)[:k]
        idcg = sum(
            rel / np.log2(i + 2)
            for i, rel in enumerate(ideal_relevances)
        )
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    @staticmethod
    def mean_average_precision(
        recommended: List[int],
        relevant: Set[int]
    ) -> float:
        """
        Calculate Mean Average Precision (MAP)
        
        Args:
            recommended: List of recommended item IDs
            relevant: Set of relevant item IDs
        
        Returns:
            MAP score
        """
        if not recommended or not relevant:
            return 0.0
        
        relevant_count = 0
        precision_sum = 0.0
        
        for i, item_id in enumerate(recommended):
            if item_id in relevant:
                relevant_count += 1
                precision_at_i = relevant_count / (i + 1)
                precision_sum += precision_at_i
        
        if relevant_count == 0:
            return 0.0
        
        return precision_sum / len(relevant)
    
    @staticmethod
    def hit_rate_at_k(
        recommended: List[int],
        relevant: Set[int],
        k: int = 10
    ) -> float:
        """
        Calculate Hit Rate@K (whether any relevant item is in top-k)
        
        Args:
            recommended: List of recommended item IDs
            relevant: Set of relevant item IDs
            k: Number of top items to consider
        
        Returns:
            1.0 if hit, 0.0 otherwise
        """
        if not recommended or not relevant:
            return 0.0
        
        top_k = set(recommended[:k])
        return 1.0 if len(top_k & relevant) > 0 else 0.0
    
    @staticmethod
    def diversity_score(
        recommended: List[int],
        item_features: Dict[int, Set[str]]
    ) -> float:
        """
        Calculate diversity score based on feature overlap
        
        Args:
            recommended: List of recommended item IDs
            item_features: Dict mapping item ID to set of features (genres, etc.)
        
        Returns:
            Diversity score (0-1, higher is more diverse)
        """
        if len(recommended) < 2:
            return 1.0
        
        # Calculate pairwise dissimilarity
        dissimilarities = []
        
        for i in range(len(recommended)):
            for j in range(i + 1, len(recommended)):
                item_i = recommended[i]
                item_j = recommended[j]
                
                if item_i in item_features and item_j in item_features:
                    features_i = item_features[item_i]
                    features_j = item_features[item_j]
                    
                    if features_i and features_j:
                        # Jaccard distance
                        intersection = len(features_i & features_j)
                        union = len(features_i | features_j)
                        similarity = intersection / union if union > 0 else 0
                        dissimilarity = 1 - similarity
                        dissimilarities.append(dissimilarity)
        
        if not dissimilarities:
            return 0.0
        
        return np.mean(dissimilarities)
    
    @staticmethod
    def coverage(
        all_recommendations: List[List[int]],
        catalog_size: int
    ) -> float:
        """
        Calculate catalog coverage
        
        Args:
            all_recommendations: List of recommendation lists for all users
            catalog_size: Total number of items in catalog
        
        Returns:
            Coverage score (0-1)
        """
        if not all_recommendations or catalog_size == 0:
            return 0.0
        
        # Get unique recommended items
        unique_items = set()
        for recommendations in all_recommendations:
            unique_items.update(recommendations)
        
        return len(unique_items) / catalog_size


class ABTestMetrics:
    """Metrics for A/B testing recommendation algorithms"""
    
    @staticmethod
    def click_through_rate(clicks: int, impressions: int) -> float:
        """Calculate CTR"""
        if impressions == 0:
            return 0.0
        return clicks / impressions
    
    @staticmethod
    def conversion_rate(conversions: int, clicks: int) -> float:
        """Calculate conversion rate"""
        if clicks == 0:
            return 0.0
        return conversions / clicks
    
    @staticmethod
    def average_watch_time(watch_times: List[float]) -> float:
        """Calculate average watch time"""
        if not watch_times:
            return 0.0
        return np.mean(watch_times)
    
    @staticmethod
    def engagement_rate(
        interactions: int,
        recommendations: int
    ) -> float:
        """Calculate engagement rate"""
        if recommendations == 0:
            return 0.0
        return interactions / recommendations


def evaluate_recommendations(
    recommended: List[int],
    relevant: Set[int],
    k_values: List[int] = [5, 10, 20]
) -> Dict[str, float]:
    """
    Evaluate recommendations with multiple metrics
    
    Args:
        recommended: List of recommended item IDs
        relevant: Set of relevant item IDs
        k_values: List of k values to evaluate
    
    Returns:
        Dict of metric names to scores
    """
    metrics = RecommendationMetrics()
    results = {}
    
    for k in k_values:
        results[f'precision@{k}'] = metrics.precision_at_k(recommended, relevant, k)
        results[f'recall@{k}'] = metrics.recall_at_k(recommended, relevant, k)
        results[f'hit_rate@{k}'] = metrics.hit_rate_at_k(recommended, relevant, k)
    
    # MAP
    results['map'] = metrics.mean_average_precision(recommended, relevant)
    
    return results
