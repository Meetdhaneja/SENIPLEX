"""
Seed database with movies from Netflix_dataset_cleaned.csv
Includes real posters fetched using the movieposters package.
"""
import csv
import os
import re
import concurrent.futures
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from loguru import logger
import movieposters as mp

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
    rating_map = {
        "TV-MA": 8.5, "TV-14": 7.8, "TV-PG": 7.5, "TV-G": 7.0, "TV-Y": 6.5,
        "TV-Y7": 6.8, "PG-13": 7.9, "PG": 7.5, "G": 7.0, "R": 8.0, "NC-17": 7.0,
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
    if not name: return None
    country = db.query(Country).filter(Country.name == name).first()
    if not country:
        country = Country(name=name)
        db.add(country)
        db.flush()
    return country


def map_genres(db: Session, listed_in: str) -> list:
    genres = []
    seen = set()
    for raw in listed_in.split(","):
        raw = raw.strip().lower()
        mapped = GENRE_MAP.get(raw)
        if mapped and mapped not in seen:
            genres.append(get_or_create_genre(db, mapped))
            seen.add(mapped)
    return genres

def fetch_poster_safe(title: str):
    """Fetch poster URL for a title with error handling"""
    try:
        url = mp.get_poster(title)
        if url and url.startswith("http"):
            return url
    except Exception as e:
        logger.debug(f"Failed to fetch poster for {title}: {e}")
    
    # Elegant fallback SVG/Placeholder if scraping fails
    clean_title = title.replace(" ", "+")
    return f"https://via.placeholder.com/300x450/1a1a2e/ffffff?text={clean_title}"

def seed_from_csv(db: Session, max_rows: int = 200):
    """Load movies from CSV into database with real posters"""
    # Check if already seeded (look for movies with non-placeholder posters or just count)
    count = db.query(Movie).count()
    if count > 20: 
        logger.info(f"Movies already seeded ({count} found), skipping CSV seed")
        return

    if not os.path.exists(CSV_PATH):
        logger.warning(f"CSV not found at {CSV_PATH}")
        return

    logger.info(f"Seeding from CSV with real posters (up to {max_rows} movies)...")
    
    # Pre-read CSV to get titles for bulk poster fetching
    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows: break
            rows.append(row)

    # Parallel poster fetching
    titles = [r.get("title", "").strip() for r in rows]
    logger.info(f"Fetching {len(titles)} posters in parallel...")
    
    poster_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_title = {executor.submit(fetch_poster_safe, title): title for title in titles if title}
        for future in concurrent.futures.as_completed(future_to_title):
            title = future_to_title[future]
            try:
                url = future.result()
                poster_map[title] = url
            except Exception:
                poster_map[title] = f"https://via.placeholder.com/300x450/1a1a2e/ffffff?text={title.replace(' ', '+')}"

    logger.info("Done fetching posters. Inserting into database...")

    loaded = 0
    for row in rows:
        try:
            title = row.get("title", "").strip()
            if not title: continue

            content_type = "TV Show" if row.get("type") == "TV Show" else "Movie"
            description = row.get("description", "").strip() or None
            release_year = int(row.get("release_year")) if row.get("release_year", "").isdigit() else None
            duration_minutes = parse_duration(row.get("duration", ""))
            numeric_rating = map_rating(row.get("rating", ""))
            
            # Use fetched poster or fallback
            thumbnail_url = poster_map.get(title)

            movie = Movie(
                title=title,
                description=description,
                release_year=release_year,
                duration_minutes=duration_minutes,
                rating=round(numeric_rating, 1),
                imdb_rating=round(numeric_rating - 0.2, 1),
                content_type=content_type,
                director=row.get("director", "").strip() or None,
                cast=row.get("cast", "").strip() or None,
                thumbnail_url=thumbnail_url,
                is_featured=(loaded < 30),
                is_active=True,
                view_count=0,
            )

            # Genres
            movie.genres = map_genres(db, row.get("listed_in", ""))
            
            # Country
            country_str = row.get("country", "").strip()
            if country_str:
                country_name = country_str.split(",")[0].strip()
                country_obj = get_or_create_country(db, country_name)
                if country_obj:
                    movie.countries = [country_obj]

            db.add(movie)
            loaded += 1
            if loaded % 50 == 0:
                db.flush()
                logger.info(f"Inserted {loaded} movies...")

        except Exception as e:
            logger.warning(f"Error for movie {row.get('title')}: {e}")
            db.rollback()

    db.commit()
    logger.info(f"CSV Seeding complete! Loaded: {loaded}")

def run():
    db = SessionLocal()
    try:
        seed_from_csv(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
