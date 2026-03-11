"""
FAISS Search
Fast similarity search using FAISS index
"""
import faiss
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from loguru import logger

from app.ai.faiss.build_index import FAISSIndexBuilder


class FAISSSearch:
    """Fast similarity search using FAISS"""
    
    def __init__(self, index_path: str = "app/ai/faiss/index_store/memax_movie.index"):
        self.builder = FAISSIndexBuilder(index_path)
        self.builder.load_index()
    
    def search_similar(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Tuple[int, float]]:
        """
        Search for similar movies using embedding
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            exclude_ids: Movie IDs to exclude from results
        
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        try:
            if self.builder.index is None:
                logger.error("FAISS index not loaded")
                return []
            
            # Normalize query embedding
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_embedding)
            
            # Search with extra results to account for exclusions
            search_k = k + len(exclude_ids) if exclude_ids else k
            search_k = min(search_k * 2, self.builder.index.ntotal)
            
            # Perform search
            distances, indices = self.builder.index.search(query_embedding, search_k)
            
            # Convert to movie IDs and scores
            results = []
            exclude_set = set(exclude_ids) if exclude_ids else set()
            
            for idx, score in zip(indices[0], distances[0]):
                if idx < len(self.builder.movie_ids):
                    movie_id = self.builder.movie_ids[idx]
                    
                    # Skip excluded movies
                    if movie_id in exclude_set:
                        continue
                    
                    results.append((movie_id, float(score)))
                    
                    if len(results) >= k:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS index: {str(e)}")
            return []
    
    def search_batch(
        self,
        query_embeddings: np.ndarray,
        k: int = 10
    ) -> List[List[Tuple[int, float]]]:
        """
        Batch search for multiple queries
        
        Args:
            query_embeddings: Array of query embeddings (n_queries, dimension)
            k: Number of results per query
        
        Returns:
            List of result lists, one per query
        """
        try:
            if self.builder.index is None:
                logger.error("FAISS index not loaded")
                return []
            
            # Normalize query embeddings
            query_embeddings = query_embeddings.astype(np.float32)
            faiss.normalize_L2(query_embeddings)
            
            # Perform batch search
            distances, indices = self.builder.index.search(query_embeddings, k)
            
            # Convert to movie IDs and scores
            all_results = []
            for query_distances, query_indices in zip(distances, indices):
                results = []
                for idx, score in zip(query_indices, query_distances):
                    if idx < len(self.builder.movie_ids):
                        movie_id = self.builder.movie_ids[idx]
                        results.append((movie_id, float(score)))
                all_results.append(results)
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in batch search: {str(e)}")
            return []
    
    def get_movie_neighbors(
        self,
        movie_id: int,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Get k nearest neighbors for a movie
        
        Args:
            movie_id: Movie ID to find neighbors for
            k: Number of neighbors to return
        
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        try:
            # Find movie index
            if movie_id not in self.builder.movie_ids:
                logger.warning(f"Movie {movie_id} not in index")
                return []
            
            movie_idx = self.builder.movie_ids.index(movie_id)
            
            # Get movie embedding from index
            movie_embedding = self.builder.index.reconstruct(movie_idx)
            
            # Search for similar movies (excluding itself)
            return self.search_similar(
                movie_embedding,
                k=k+1,
                exclude_ids=[movie_id]
            )[:k]
            
        except Exception as e:
            logger.error(f"Error getting movie neighbors: {str(e)}")
            return []
    
    def reload_index(self) -> bool:
        """Reload FAISS index from disk"""
        return self.builder.load_index()


# Global search instance
_search_instance: Optional[FAISSSearch] = None


def get_search_instance() -> FAISSSearch:
    """Get or create global FAISS search instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = FAISSSearch()
    return _search_instance


def search_similar_movies(
    query_embedding: np.ndarray,
    k: int = 10,
    exclude_ids: Optional[List[int]] = None
) -> List[Tuple[int, float]]:
    """Convenience function for similarity search"""
    searcher = get_search_instance()
    return searcher.search_similar(query_embedding, k, exclude_ids)
