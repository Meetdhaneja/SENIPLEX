"""
Admin UI Routes
Backend admin interface routes
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

import os
import time
from app.db.session import get_db
from app.models.user import User
from app.models.movie import Movie
from app.models.interaction import Interaction
from app.routes.auth import get_current_user
from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.services.user_service import get_user_by_email
from app.ai.faiss.build_index import FAISSIndexBuilder

router = APIRouter()

# Templates
try:
    templates = Jinja2Templates(directory="app/templates")
except:
    templates = None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if not templates:
        return {"message": "Templates not configured"}
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Depends(lambda r: r.form().get("username")),
    password: str = Depends(lambda r: r.form().get("password")),
    db: Session = Depends(get_db)
):
    """Admin login handler"""
    user = get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password) or not user.is_admin:
        if not templates:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        return templates.TemplateResponse("admin/login.html", {
            "request": request, 
            "error": "Invalid admin credentials or not an admin."
        })
    
    # Create token & redirect
    access_token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=3600*24
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin dashboard home"""
    if not templates:
        return {"message": "Templates not configured. Use /api/admin for API access."}
    
    if not current_user.is_admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    # Get stats
    total_users = db.query(User).count()
    total_movies = db.query(Movie).count()
    total_interactions = db.query(Interaction).count()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_users": total_users,
        "total_movies": total_movies,
        "total_interactions": total_interactions,
        "user": current_user
    })


@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin users page"""
    if not current_user.is_admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    users = db.query(User).limit(100).all()
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "users": users,
        "user": current_user
    })


@router.get("/movies", response_class=HTMLResponse)
async def admin_movies(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin movies page"""
    if not current_user.is_admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    movies = db.query(Movie).limit(100).all()
    
    return templates.TemplateResponse("admin/movies.html", {
        "request": request,
        "movies": movies,
        "user": current_user
    })


@router.get("/movies/add", response_class=HTMLResponse)
async def admin_movies_add(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Admin movies add page"""
    if not current_user.is_admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates.TemplateResponse("admin/movies_add.html", {
        "request": request,
        "user": current_user
    })


@router.get("/analytics", response_class=HTMLResponse)
async def admin_analytics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin analytics page"""
    if not current_user.is_admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates.TemplateResponse("admin/analytics.html", {
        "request": request,
        "user": current_user
    })


@router.get("/models", response_class=HTMLResponse)
async def admin_models(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin AI models page"""
    if not current_user.is_admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    # Check FAISS status
    index_path = "app/ai/faiss/index_store/memax_movie.index"
    index_exists = os.path.exists(index_path)
    index_time = os.path.getmtime(index_path) if index_exists else 0
    
    # Check database embeddings
    from app.models.movie_embeddings import MovieEmbedding
    embedding_count = db.query(MovieEmbedding).count()
    
    return templates.TemplateResponse("admin/models.html", {
        "request": request,
        "index_exists": index_exists,
        "index_time": time.ctime(index_time) if index_time else "N/A",
        "embedding_count": embedding_count,
        "user": current_user
    })


@router.post("/models/rebuild")
async def rebuild_models(
    current_user: User = Depends(get_current_user)
):
    """Trigger FAISS index rebuild"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
        
    builder = FAISSIndexBuilder()
    success = builder.build_index()
    
    return RedirectResponse(url="/admin/models?status=" + ("success" if success else "failed"), status_code=303)
