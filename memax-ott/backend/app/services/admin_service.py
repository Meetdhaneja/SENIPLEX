"""Admin service"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.user import User
from app.models.movie import Movie
from app.models.watch_history import WatchHistory
from app.models.interaction import Interaction
from app.schemas.admin_schema import AdminStats, AdminUserResponse


def get_admin_stats(db: Session) -> AdminStats:
    """Get admin statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_movies = db.query(Movie).count()
    total_views = db.query(WatchHistory).count()
    total_interactions = db.query(Interaction).count()
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_movies=total_movies,
        total_views=total_views,
        total_interactions=total_interactions
    )


def get_all_users(db: Session) -> List[AdminUserResponse]:
    """Get all users with stats"""
    users = db.query(User).all()
    result = []
    
    for user in users:
        total_watch_time = db.query(func.sum(WatchHistory.watch_duration_seconds)).filter(
            WatchHistory.user_id == user.id
        ).scalar() or 0
        
        total_interactions = db.query(Interaction).filter(Interaction.user_id == user.id).count()
        
        result.append(AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            total_watch_time=total_watch_time,
            total_interactions=total_interactions
        ))
    
    return result
