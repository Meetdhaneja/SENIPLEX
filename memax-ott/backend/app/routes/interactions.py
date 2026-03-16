"""Interaction routes"""
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.interaction_schema import (
    InteractionCreate, InteractionResponse,
    WatchProgressCreate, WatchProgressResponse
)
from app.services.interaction_service import (
    create_interaction, get_user_interactions,
    create_or_update_watch_progress, get_user_watch_progress
)
from app.routes.auth import get_current_user

router = APIRouter()


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def record_interaction(
    interaction_data: InteractionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record user interaction with movie"""
    return create_interaction(db, current_user.id, interaction_data, background_tasks)


@router.get("", response_model=List[InteractionResponse])
async def list_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's interactions"""
    return get_user_interactions(db, current_user.id)


@router.post("/progress", response_model=WatchProgressResponse)
async def update_watch_progress(
    progress_data: WatchProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update watch progress"""
    return create_or_update_watch_progress(db, current_user.id, progress_data)


@router.get("/progress", response_model=List[WatchProgressResponse])
async def list_watch_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's watch progress (continue watching)"""
    return get_user_watch_progress(db, current_user.id)
