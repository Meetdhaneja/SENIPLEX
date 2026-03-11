"""Seed database with initial data"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.genre import Genre
from app.models.country import Country
from app.core.security import get_password_hash
from app.core.config import settings
from loguru import logger


def seed_admin_user(db: Session):
    """Create admin user"""
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists")


def seed_genres(db: Session):
    """Create default genres"""
    genres = [
        "Action", "Comedy", "Drama", "Horror", "Thriller",
        "Romance", "Sci-Fi", "Fantasy", "Documentary", "Animation",
        "Crime", "Mystery", "Adventure", "Family", "War"
    ]
    
    for genre_name in genres:
        genre = db.query(Genre).filter(Genre.name == genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.add(genre)
    
    db.commit()
    logger.info(f"Seeded {len(genres)} genres")


def seed_countries(db: Session):
    """Create default countries"""
    countries = [
        "United States", "United Kingdom", "India", "Canada", "Australia",
        "France", "Germany", "Japan", "South Korea", "Spain",
        "Italy", "Brazil", "Mexico", "China", "Russia"
    ]
    
    for country_name in countries:
        country = db.query(Country).filter(Country.name == country_name).first()
        if not country:
            country = Country(name=country_name)
            db.add(country)
    
    db.commit()
    logger.info(f"Seeded {len(countries)} countries")


def seed_database():
    """Seed all initial data"""
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_genres(db)
        seed_countries(db)
        logger.info("Database seeding completed")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
