"""
Seed database with movies from Netflix_dataset_cleaned.csv
Parses the CSV and loads up to 500 movies into the database.
"""
import csv
import os
import re
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from loguru import logger

CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/raw/Netflix_dataset_cleaned.csv")

# Map Netflix genres to our genre names
GENRE_MAP = {
    "action": "Action",
    "comedy": "Comedy", "comedies": "Comedy",
    "drama": "Drama", "dramas": "Drama",
    "horror": "Horror", "horror movies": "Horror",
    "thriller": "Thriller", "thrillers": "Thriller",
    "romance": "Romance", "romantic": "Romance", "romantic movies": "Romance",
    "sci-fi": "Sci-Fi", "sci-fi & fantasy": "Sci-Fi", "science & nature tv": "Documentary",
    "fantasy": "Fantasy",
    "documentary": "Documentary", "documentaries": "Documentary", "docuseries": "Documentary",
    "anime": "Adventure", "anime series": "Sci-Fi", "anime features": "Sci-Fi",
    "animation": "Animation",
    "crime": "Crime", "crime tv shows": "Crime",
    "mystery": "Mystery", "tv mysteries": "Mystery",
    "adventure": "Adventure",
    "children": "Family", "family movies": "Family", "kids' tv": "Family",
    "war": "War",
}

def parse_duration(duration_str: str) -> int:
    """Parse '90 min' or '2 seasons' to integer minutes"""
    if not duration_str:
        return None
    duration_str = duration_str.strip()
    if "min" in duration_str:
        match = re.search(r"(\d+)", duration_str)
        if match:
            return int(match.group(1))
    elif "season" in duration_str:
        match = re.search(r"(\d+)", duration_str)
        if match:
            return int(match.group(1)) * 60  # approximate
    return None


def map_rating(rating_str: str) -> float:
    """Map content rating string to a numeric rating"""
    rating_map = {
        "TV-MA": 8.5,
        "TV-14": 7.8,
        "TV-PG": 7.5,
        "TV-G": 7.0,
        "TV-Y": 6.5,
        "TV-Y7": 6.8,
        "PG-13": 7.9,
        "PG": 7.5,
        "G": 7.0,
        "R": 8.0,
        "NC-17": 7.0,
    }
    return rating_map.get(rating_str.strip() if rating_str else "", 7.5)


def get_or_create_genre(db: Session, name: str) -> Genre:
    genre = db.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    return genre


def get_or_create_country(db: Session, name: str) -> Country:
    name = name.strip()
    if not name:
        return None
    country = db.query(Country).filter(Country.name == name).first()
    if not country:
        country = Country(name=name)
        db.add(country)
        db.flush()
    return country


def map_genres(db: Session, listed_in: str) -> list:
    """Map CSV 'listed_in' to Genre objects"""
    genres = []
    seen = set()
    for raw in listed_in.split(","):
        raw = raw.strip().lower()
        mapped = GENRE_MAP.get(raw)
        if mapped and mapped not in seen:
            genres.append(get_or_create_genre(db, mapped))
            seen.add(mapped)
    return genres


def seed_from_csv(db: Session, max_rows: int = 500):
    """Load movies from CSV into database"""
    count = db.query(Movie).count()
    if count > 20:
        logger.info(f"Movies already seeded from CSV ({count} found), skipping")
        return

    if not os.path.exists(CSV_PATH):
        logger.warning(f"CSV not found at {CSV_PATH}, skipping CSV seed")
        return

    logger.info(f"Seeding from CSV: {CSV_PATH}")
    loaded = 0
    skipped = 0

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if loaded >= max_rows:
                break
            try:
                title = row.get("title", "").strip()
                if not title:
                    skipped += 1
                    continue

                content_type_raw = row.get("type", "Movie").strip()
                content_type = "TV Show" if content_type_raw == "TV Show" else "Movie"

                description = row.get("description", "").strip() or None
                release_year_str = row.get("release_year", "").strip()
                release_year = int(release_year_str) if release_year_str.isdigit() else None
                duration_minutes = parse_duration(row.get("duration", ""))
                rating_str = row.get("rating", "").strip()
                numeric_rating = map_rating(rating_str)
                director = row.get("director", "").strip() or None
                cast = row.get("cast", "").strip() or None
                
                # Country
                country_str = row.get("country", "").strip()
                country_name = country_str.split(",")[0].strip() if country_str else None

                listed_in = row.get("listed_in", "").strip()
                genres = map_genres(db, listed_in)

                # Mark first 30 as featured for hero carousel
                is_featured = (loaded < 30 and release_year and release_year >= 2019)

                # TMDB-style placeholder thumbnail
                thumbnail_url = f"https://via.placeholder.com/300x450/1a1a2e/ffffff?text={title[:20].replace(' ', '+')}"

                movie = Movie(
                    title=title,
                    description=description,
                    release_year=release_year,
                    duration_minutes=duration_minutes,
                    rating=round(numeric_rating, 1),
                    imdb_rating=round(numeric_rating - 0.2, 1),
                    content_type=content_type,
                    director=director,
                    cast=cast,
                    thumbnail_url=thumbnail_url,
                    is_featured=is_featured,
                    is_active=True,
                    view_count=0,
                )

                if genres:
                    movie.genres = genres

                if country_name:
                    country_obj = get_or_create_country(db, country_name)
                    if country_obj:
                        movie.countries = [country_obj]

                db.add(movie)
                loaded += 1

                if loaded % 50 == 0:
                    db.flush()
                    logger.info(f"Loaded {loaded} movies so far...")

            except Exception as e:
                skipped += 1
                logger.warning(f"Skipped row {i}: {e}")
                db.rollback()
                continue

    db.commit()
    logger.info(f"CSV Seeding complete! Loaded: {loaded}, Skipped: {skipped}")


def run():
    db = SessionLocal()
    try:
        seed_from_csv(db)
    except Exception as e:
        logger.error(f"CSV seed failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run()
