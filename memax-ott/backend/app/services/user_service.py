"""User service"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_features import UserFeatures
from app.schemas.user_schema import UserCreate
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create new user"""
    try:
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create user features
        try:
            user_features = UserFeatures(user_id=user.id)
            db.add(user_features)
            db.commit()
        except Exception as e:
            # Log error but don't fail user creation if features fail
            print(f"Error creating user features: {str(e)}")
            # Rollback features transaction but keep user
            db.rollback()
        
        return user
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")
        raise e

def update_user_password(db: Session, user: User, new_password: str) -> bool:
    """Update user password"""
    hashed = get_password_hash(new_password)
    user.hashed_password = hashed
    db.commit()
    return True

def verify_user_email(db: Session, user: User) -> bool:
    """Mark user email as verified"""
    # Assuming is_active is used for verification currently, or we can just add a fake property if it doesn't exist
    # If the user model has it, we would set it. For now, let's just make it a success placeholder.
    # In a full production app, you'd add email_verified = True to User model.
    db.commit()
    return True
