"""Analytics routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.models.user import User
from app.routes.auth import get_current_user

router = APIRouter()


@router.get("/user-stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user statistics"""
    from app.models.watch_history import WatchHistory
    from app.models.interaction import Interaction
    
    total_watched = db.query(WatchHistory).filter(WatchHistory.user_id == current_user.id).count()
    total_interactions = db.query(Interaction).filter(Interaction.user_id == current_user.id).count()
    
    return {
        "total_watched": total_watched,
        "total_interactions": total_interactions,
        "user_id": current_user.id
    }
