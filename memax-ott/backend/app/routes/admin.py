"""Admin routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_schema import AdminStats, AdminUserResponse
from app.services.admin_service import get_admin_stats, get_all_users
from app.routes.auth import get_current_user

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin access"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get platform statistics"""
    return get_admin_stats(db)


from fastapi import File, UploadFile, Form
import shutil
import os

@router.get("/users", response_model=List[AdminUserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users"""
    return get_all_users(db)


@router.post("/movies/upload")
async def upload_movie(
    title: str = Form(...),
    description: str = Form(...),
    cast: str = Form(""),
    director: str = Form(""),
    genres: str = Form(""),
    countries: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Secure Administration CMS - Upload 8GB Movie File and Publish Metadata"""
    
    # In a full-scale Production OTT, you would NEVER save an 8GB file locally like this.
    # Instead, you would upload it via Multi-Part Upload to AWS S3, and trigger AWS MediaConvert
    # to transcode the video into HLS streams (1080p, 720p chunks).
    # This is a local abstraction to represent the ingestion endpoint.
    
    import loguru
    loguru.logger.info(f"ADMIN CMS: Publishing {title} by {director}")
    
    # 1. Create secure file path (Simulating S3 bucket stream)
    upload_dir = "uploads/movies"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = f"{upload_dir}/{file.filename}"
    
    with open(file_location, "wb+") as file_object:
        # Saving in chunks to avoid memory crash
        shutil.copyfileobj(file.file, file_object)
        
    # 2. Add Database Entry
    from app.models.movie import Movie
    new_movie = Movie(
        title=title,
        description=description,
        cast=cast,
        director=director,
        content_type="movie",
        videoUrl=f"/api/movies/stream/{file.filename}"  # Placeholder for HLS manifest URL
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    
    # NOTE: You would assign genres/countries via junction tables here as well
    # for name in genres.split(","): 
    #     g = get_genre(name) 
    #     new_movie.genres.append(g)
    
    return {"message": f"Successfully published {title} to the platform!", "movie_id": new_movie.id}
