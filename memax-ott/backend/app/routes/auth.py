"""Authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, Token, UserLogin
from app.core.security import verify_password, get_password_hash
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.services.user_service import create_user, get_user_by_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    request: Request = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try getting token from cookie if not in header
    if not token and request:
        token = request.cookies.get("access_token")
        
    if not token:
        raise credentials_exception
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if email exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    # Note: We need to import get_user_by_username first or use db query directly
    # To keep it safe, let's query directly here if the function import is tricky or assume we imported it
    # But since we just added it to user_service, let's update the import
    from app.services.user_service import get_user_by_username
    existing_username = get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    try:
        user = create_user(db, user_data)
        return user
    except Exception as e:
        # Catch any other error (like database integrity error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


from app.schemas.user_schema import PasswordResetRequest, PasswordResetConfirm, MessageResponse
from app.services.user_service import update_user_password, verify_user_email

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Generate a password reset token (mock email send)"""
    user = get_user_by_email(db, request.email)
    if not user:
        # Don't leak whether the email exists or not
        return {"message": "If that email exists, a reset link has been sent."}
    
    # Generate a temporary reset token (in production, email this)
    reset_token = create_access_token(data={"sub": str(user.id), "type": "reset"}, expires_delta=timedelta(hours=1))
    
    # MOCK: Log it instead of sending email via SendGrid/SES
    import loguru
    loguru.logger.info(f"MOCK EMAIL SENT TO {user.email} -> Reset Token: {reset_token}")
    
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset the password using the token sent to email"""
    payload = decode_token(request.token)
    if not payload or payload.get("type") != "reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload")
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    update_user_password(db, user, request.new_password)
    return {"message": "Password updated successfully"}


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user's email"""
    payload = decode_token(token)
    if not payload or payload.get("type") != "verify":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")
        
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    verify_user_email(db, user)
    return {"message": "Email previously verified successfully"}
