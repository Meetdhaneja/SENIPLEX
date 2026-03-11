"""
Feature Updater
Periodically update user and movie features
"""
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.db.session import SessionLocal
from app.feature_store.user_features import UserFeatureExtractor
from app.feature_store.movie_features import MovieFeatureExtractor
from app.models.user import User
from app.models.movie import Movie


class FeatureUpdater:
    """Update features for users and movies"""
    
    def __init__(self):
        self.user_extractor = UserFeatureExtractor()
        self.movie_extractor = MovieFeatureExtractor()
    
    def update_user_features(
        self,
        user_ids: List[int] = None,
        db: Session = None
    ) -> int:
        """
        Update features for users
        
        Args:
            user_ids: Optional list of specific user IDs to update
            db: Database session
        
        Returns:
            Number of users updated
        """
        db = db or SessionLocal()
        updated_count = 0
        
        try:
            # Get users to update
            if user_ids:
                users = db.query(User).filter(User.id.in_(user_ids)).all()
            else:
                # Update active users
                users = db.query(User).filter(User.is_active == True).all()
            
            logger.info(f"Updating features for {len(users)} users")
            
            for user in users:
                try:
                    # Extract features
                    features = self.user_extractor.extract_features(user.id, db)
                    
                    # Store features (you can add a UserFeatures model if needed)
                    # For now, just log
                    logger.debug(f"Updated features for user {user.id}")
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating features for user {user.id}: {str(e)}")
                    continue
            
            logger.info(f"Updated features for {updated_count} users")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error in user feature update: {str(e)}")
            return updated_count
        finally:
            if db:
                db.close()
    
    def update_movie_features(
        self,
        movie_ids: List[int] = None,
        db: Session = None
    ) -> int:
        """
        Update features for movies
        
        Args:
            movie_ids: Optional list of specific movie IDs to update
            db: Database session
        
        Returns:
            Number of movies updated
        """
        db = db or SessionLocal()
        updated_count = 0
        
        try:
            # Get movies to update
            if movie_ids:
                movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            else:
                # Update active movies
                movies = db.query(Movie).filter(Movie.is_active == True).all()
            
            logger.info(f"Updating features for {len(movies)} movies")
            
            for movie in movies:
                try:
                    # Extract features
                    features = self.movie_extractor.extract_features(movie.id, db)
                    
                    # Store features (you can add a MovieFeatures model if needed)
                    logger.debug(f"Updated features for movie {movie.id}")
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating features for movie {movie.id}: {str(e)}")
                    continue
            
            logger.info(f"Updated features for {updated_count} movies")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error in movie feature update: {str(e)}")
            return updated_count
        finally:
            if db:
                db.close()
    
    def update_all_features(self, db: Session = None) -> dict:
        """
        Update all user and movie features
        
        Returns:
            Dict with update counts
        """
        logger.info("Starting full feature update")
        
        user_count = self.update_user_features(db=db)
        movie_count = self.update_movie_features(db=db)
        
        return {
            'users_updated': user_count,
            'movies_updated': movie_count,
            'timestamp': datetime.utcnow()
        }


def update_features_for_user(user_id: int, db: Session = None):
    """Convenience function to update features for single user"""
    updater = FeatureUpdater()
    return updater.update_user_features([user_id], db)


def update_features_for_movie(movie_id: int, db: Session = None):
    """Convenience function to update features for single movie"""
    updater = FeatureUpdater()
    return updater.update_movie_features([movie_id], db)
