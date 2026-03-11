from app.db.session import SessionLocal
from app.services.user_service import create_user
from app.schemas.user_schema import UserCreate
from app.models.user import User
import uuid

def test_user_creation():
    db = SessionLocal()
    try:
        # Create unique email/username
        uid = str(uuid.uuid4())[:8]
        user_data = UserCreate(
            email=f"test_{uid}@example.com",
            username=f"test_{uid}",
            password="testpassword123",
            full_name="Test User"
        )
        
        print(f" अटेmpting to create user: {user_data.username}")
        user = create_user(db, user_data)
        print(f"✅ User created successfully! ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_creation()
