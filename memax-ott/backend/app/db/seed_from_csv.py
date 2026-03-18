"""
Seed database with ALL movies from Netflix_dataset_cleaned.csv
Optimized for high volume (8000+) and maximum metadata coverage.
"""
import csv
import os
import re
import random
import concurrent.futures
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from loguru import logger
import movieposters as mp

def get_default_csv_path() -> str:
    # Support explicit override from environment (e.g. "C:\\Users\\Dell\\Downloads\\Netflix Datasets.csv")
    override = os.getenv("NETFLIX_DATASET_CSV_PATH") or os.getenv("NETFLIX_CSV_PATH")
    if override:
        return override
    return os.path.join(os.path.dirname(__file__), "../data/raw/Netflix_dataset_cleaned.csv")

# Global caches to avoid redundant DB queries during massive seeding
_GENRE_CACHE = {}
_COUNTRY_CACHE = {}

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
    if name in _GENRE_CACHE:
        return _GENRE_CACHE[name]
    
    genre = db.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    
    _GENRE_CACHE[name] = genre
    return genre

def get_or_create_country(db: Session, name: str) -> Country:
    name = name.strip()
    if not name: return None
    
    if name in _COUNTRY_CACHE:
        return _COUNTRY_CACHE[name]
        
    country = db.query(Country).filter(Country.name == name).first()
    if not country:
        country = Country(name=name)
        db.add(country)
        db.flush()
    
    _COUNTRY_CACHE[name] = country
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
    except Exception:
        pass
    
    # Stylized fallback for better appearance
    clean_title = title.replace(" ", "+")
    colors = ["1a1a2e", "16213e", "0f3460", "533483"]
    color = random.choice(colors)
    return f"https://via.placeholder.com/400x600/{color}/ffffff?text={clean_title}"

def seed_from_csv(db: Session, max_rows: int = 10000, csv_path: str = None):
    """Load movies from CSV into database with high speed and low memory"""
    if csv_path is None:
        csv_path = get_default_csv_path()

    # 1. Warm up caches
    try:
        for g in db.query(Genre).all(): _GENRE_CACHE[g.name] = g
        for c in db.query(Country).all(): _COUNTRY_CACHE[c.name] = c
        logger.info(f"Caches warmed: {len(_GENRE_CACHE)} genres, {len(_COUNTRY_CACHE)} countries.")
    except Exception:
        logger.warning("Caches couldn't be warmed. Proceeding.")

    # 2. Check current count
    try:
        count = db.query(Movie).count()
        if count >= 8000:
            logger.info(f"Database already has {count} movies. Skipping full reload.")
            return
    except Exception:
        logger.info("Database table not ready or empty. Starting fresh seeding.")

    if not os.path.exists(csv_path):
        logger.warning(f"CSV not found at {csv_path}")
        return

    logger.info(f"Seeding FULL dataset from CSV {csv_path} (up to {max_rows} rows)...")
    
    # 3. Stream processing
    BATCH_SIZE = 200
    total_loaded = 0
    existing_movies = set()
    
    try:
        # Pre-fetch existing (title, year) pairs
        existing_movies = set(db.query(Movie.title, Movie.release_year).all())
        logger.info(f"Found {len(existing_movies)} existing movies. Processing only new entries.")
    except Exception:
        logger.warning("Could not pre-fetch existing movies. Proceeding row-by-row.")

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for i, row in enumerate(reader):
            if i >= max_rows: break
            
            title = row.get("title", "").strip()
            if not title: continue
            
            release_year = int(row.get("release_year")) if row.get("release_year", "").isdigit() else None
            if (title, release_year) in existing_movies:
                continue
                
            batch.append(row)
            
            if len(batch) >= BATCH_SIZE:
                # Only scrape posters for the first ~100 movies to avoid throttling
                use_scraper = (total_loaded < 100)
                total_loaded += _process_batch(db, batch, existing_movies, use_scraper)
                batch = []
                logger.info(f"Seeding Progress: {total_loaded} movies added...")
        
        # Process final batch
        if batch:
            total_loaded += _process_batch(db, batch, existing_movies, (total_loaded < 100))

    logger.info(f"Full CSV Seeding complete! Total new entries: {total_loaded}")

def _process_batch(db: Session, batch_rows: list, existing_movies: set, use_scraper: bool) -> int:
    """Helper to process a batch of CSV rows"""
    batch_loaded = 0
    poster_map = {}
    
    if use_scraper:
        # Concurrent scraping for first 100
        titles = [r.get("title", "").strip() for r in batch_rows]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_title = {executor.submit(fetch_poster_safe, t): t for t in titles if t}
            for future in concurrent.futures.as_completed(future_to_title):
                title = future_to_title[future]
                try:
                    poster_map[title] = future.result()
                except Exception:
                    poster_map[title] = None

    for row in batch_rows:
        try:
            title = row.get("title", "").strip()
            release_year = int(row.get("release_year")) if row.get("release_year", "").isdigit() else None
            
            # Final check to avoid race conditions with other threads
            if (title, release_year) in existing_movies:
                continue

            # Poster logic
            thumbnail_url = poster_map.get(title)
            if not thumbnail_url:
                # Instant Placeholder
                clean_title = title.replace(" ", "+")
                color = random.choice(["1a1a2e", "0f3460", "533483"])
                thumbnail_url = f"https://via.placeholder.com/400x600/{color}/ffffff?text={clean_title[:15]}"

            # Featured Logic: mark first few as featured so Hero isn't empty
            is_featured = (batch_loaded < 50) and (random.random() < 0.3)

            movie = Movie(
                title=title,
                description=row.get("description", "").strip() or None,
                release_year=release_year,
                duration_minutes=parse_duration(row.get("duration", "")),
                rating=round(map_rating(row.get("rating", "")), 1),
                imdb_rating=round(map_rating(row.get("rating", "")) - 0.2, 1),
                age_rating=row.get("rating", "").strip() or None,
                date_added=row.get("date_added", "").strip() or None,
                content_type="TV Show" if row.get("type") == "TV Show" else "Movie",
                director=row.get("director", "").strip() or None,
                cast=row.get("cast", "").strip() or None,
                thumbnail_url=thumbnail_url,
                is_featured=is_featured,
                is_active=True,
                view_count=random.randint(100, 500000),
            )

            movie.genres = map_genres(db, row.get("listed_in", ""))
            
            country_str = row.get("country", "").strip()
            if country_str:
                country_name = country_str.split(",")[0].strip()
                country_obj = get_or_create_country(db, country_name)
                if country_obj:
                    movie.countries = [country_obj]

            db.add(movie)
            existing_movies.add((title, release_year))
            batch_loaded += 1

        except Exception as e:
            logger.error(f"Failed row: {title} - {str(e)}")
            continue
    
    db.commit()
    return batch_loaded

def run(csv_path: str = None, max_rows: int = 10000):
    db = SessionLocal()
    try:
        seed_from_csv(db, max_rows=max_rows, csv_path=csv_path)
    finally:
        db.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed movies from a Netflix CSV dataset")
    parser.add_argument("--csv", dest="csv_path", type=str, default=None, help="CSV file path to import")
    parser.add_argument("--max", dest="max_rows", type=int, default=10000, help="Maximum number of rows to import")
    args = parser.parse_args()
    run(csv_path=args.csv_path, max_rows=args.max_rows)
