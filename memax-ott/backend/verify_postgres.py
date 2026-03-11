"""
PostgreSQL Connection Verification Script
Tests the database connection and displays status
"""

from app.db.session import engine, SessionLocal
from app.core.config import settings
from sqlalchemy import inspect, text
from loguru import logger
import sys

def verify_connection():
    """Verify PostgreSQL connection and display status"""
    
    print("=" * 60)
    print("🔍 POSTGRESQL CONNECTION VERIFICATION")
    print("=" * 60)
    print()
    
    # Test 1: Configuration
    print("✅ Step 1: Configuration")
    print(f"   Database: Netflix")
    print(f"   Host: localhost:5432")
    print(f"   App Name: {settings.APP_NAME}")
    print(f"   Debug Mode: {settings.DEBUG}")
    print()
    
    # Test 2: Connection
    print("✅ Step 2: Database Connection")
    try:
        connection = engine.connect()
        print("   ✓ Connection successful!")
        connection.close()
    except Exception as e:
        print(f"   ✗ Connection failed: {str(e)}")
        sys.exit(1)
    print()
    
    # Test 3: Tables
    print("✅ Step 3: Database Tables")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"   ✓ Found {len(tables)} tables")
        
        # Show application tables
        app_tables = [t for t in tables if t not in ['Netflix_data', 'mydata1']]
        print(f"   ✓ Application tables: {len(app_tables)}")
        for table in sorted(app_tables):
            print(f"      - {table}")
    except Exception as e:
        print(f"   ✗ Error reading tables: {str(e)}")
    print()
    
    # Test 4: Query Test
    print("✅ Step 4: Query Test")
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        db.close()
        print(f"   ✓ Query executed successfully (result: {row[0]})")
    except Exception as e:
        print(f"   ✗ Query failed: {str(e)}")
    print()
    
    # Test 5: Check existing data
    print("✅ Step 5: Data Check")
    try:
        db = SessionLocal()
        
        # Check users
        from app.models.user import User
        user_count = db.query(User).count()
        print(f"   ✓ Users: {user_count}")
        
        # Check movies
        from app.models.movie import Movie
        movie_count = db.query(Movie).count()
        print(f"   ✓ Movies: {movie_count}")
        
        # Check genres
        from app.models.genre import Genre
        genre_count = db.query(Genre).count()
        print(f"   ✓ Genres: {genre_count}")
        
        db.close()
    except Exception as e:
        print(f"   ⚠ Data check: {str(e)}")
    print()
    
    print("=" * 60)
    print("🎉 POSTGRESQL CONNECTION VERIFIED!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Start backend server: python -m uvicorn app.main:app --reload")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Test health endpoint: http://localhost:8000/health")
    print()

if __name__ == "__main__":
    verify_connection()
