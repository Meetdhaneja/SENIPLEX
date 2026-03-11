"""
Data Loader - Import Movies from CSV/JSON to Database
Supports Netflix, TMDB, and custom datasets
"""
import pandas as pd
import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from app.models.movie_embeddings import MovieEmbedding


class DataLoader:
    """Load movie data from various sources"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.genre_cache = {}
        self.country_cache = {}
        self._load_caches()
    
    def _load_caches(self):
        """Load existing genres and countries into cache"""
        genres = self.db.query(Genre).all()
        self.genre_cache = {g.name.lower(): g for g in genres}
        
        countries = self.db.query(Country).all()
        self.country_cache = {c.name.lower(): c for c in countries}
        
        logger.info(f"Loaded {len(self.genre_cache)} genres and {len(self.country_cache)} countries")
    
    def get_or_create_genre(self, genre_name: str) -> Genre:
        """Get or create a genre"""
        genre_name_lower = genre_name.strip().lower()
        
        if genre_name_lower in self.genre_cache:
            return self.genre_cache[genre_name_lower]
        
        # Create new genre
        genre = Genre(name=genre_name.strip())
        self.db.add(genre)
        self.db.flush()
        self.genre_cache[genre_name_lower] = genre
        
        logger.info(f"Created new genre: {genre_name}")
        return genre
    
    def get_or_create_country(self, country_name: str) -> Country:
        """Get or create a country"""
        country_name_lower = country_name.strip().lower()
        
        if country_name_lower in self.country_cache:
            return self.country_cache[country_name_lower]
        
        # Create new country
        country = Country(name=country_name.strip())
        self.db.add(country)
        self.db.flush()
        self.country_cache[country_name_lower] = country
        
        logger.info(f"Created new country: {country_name}")
        return country
    
    def parse_genres(self, genre_str: str) -> List[Genre]:
        """Parse genre string and return Genre objects"""
        if not genre_str or pd.isna(genre_str):
            return []
        
        # Handle different separators
        separators = [',', '|', ';', '&']
        for sep in separators:
            if sep in str(genre_str):
                genre_names = [g.strip() for g in str(genre_str).split(sep)]
                return [self.get_or_create_genre(name) for name in genre_names if name]
        
        # Single genre
        return [self.get_or_create_genre(str(genre_str))]
    
    def parse_countries(self, country_str: str) -> List[Country]:
        """Parse country string and return Country objects"""
        if not country_str or pd.isna(country_str):
            return []
        
        # Handle different separators
        separators = [',', '|', ';']
        for sep in separators:
            if sep in str(country_str):
                country_names = [c.strip() for c in str(country_str).split(sep)]
                return [self.get_or_create_country(name) for name in country_names if name]
        
        # Single country
        return [self.get_or_create_country(str(country_str))]
    
    def clean_value(self, value: Any, default: Any = None) -> Any:
        """Clean and validate value"""
        if pd.isna(value) or value == '' or value == 'N/A':
            return default
        return value
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to minutes"""
        if not duration_str or pd.isna(duration_str):
            return None
        
        duration_str = str(duration_str).lower()
        
        # Handle "120 min" format
        if 'min' in duration_str:
            try:
                return int(duration_str.replace('min', '').strip())
            except:
                pass
        
        # Handle "2h 30m" format
        if 'h' in duration_str or 'm' in duration_str:
            try:
                hours = 0
                minutes = 0
                
                if 'h' in duration_str:
                    parts = duration_str.split('h')
                    hours = int(parts[0].strip())
                    if len(parts) > 1 and 'm' in parts[1]:
                        minutes = int(parts[1].replace('m', '').strip())
                elif 'm' in duration_str:
                    minutes = int(duration_str.replace('m', '').strip())
                
                return hours * 60 + minutes
            except:
                pass
        
        # Try direct integer conversion
        try:
            return int(duration_str)
        except:
            return None
    
    def parse_rating(self, rating_str: str) -> Optional[float]:
        """Parse rating string to float"""
        if not rating_str or pd.isna(rating_str):
            return None
        
        try:
            rating = float(str(rating_str).replace('/10', '').strip())
            # Normalize to 0-10 scale
            if rating > 10:
                rating = rating / 10
            return round(rating, 1)
        except:
            return None
    
    def load_from_csv(self, csv_path: str, mapping: Dict[str, str] = None) -> int:
        """
        Load movies from CSV file
        
        Args:
            csv_path: Path to CSV file
            mapping: Column mapping dict, e.g. {'title': 'show_title', 'type': 'content_type'}
        
        Returns:
            Number of movies imported
        """
        logger.info(f"Loading data from {csv_path}")
        
        # Default column mapping for Netflix dataset
        default_mapping = {
            'title': 'title',
            'type': 'type',
            'description': 'description',
            'release_year': 'release_year',
            'duration': 'duration',
            'listed_in': 'listed_in',  # genres
            'country': 'country',
            'director': 'director',
            'cast': 'cast',
            'rating': 'rating',
            'date_added': 'date_added'
        }
        
        mapping = mapping or default_mapping
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Read {len(df)} rows from CSV")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            imported_count = 0
            skipped_count = 0
            
            for idx, row in df.iterrows():
                try:
                    # Extract data using mapping
                    title = self.clean_value(row.get(mapping.get('title', 'title')))
                    if not title:
                        logger.warning(f"Row {idx}: No title, skipping")
                        skipped_count += 1
                        continue
                    
                    # Check if movie already exists
                    existing = self.db.query(Movie).filter(Movie.title == title).first()
                    if existing:
                        logger.debug(f"Movie '{title}' already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    # Parse content type
                    content_type = self.clean_value(row.get(mapping.get('type', 'type')), 'Movie')
                    
                    # Parse duration
                    duration_str = self.clean_value(row.get(mapping.get('duration', 'duration')))
                    duration_minutes = self.parse_duration(duration_str)
                    
                    # Parse rating
                    rating_str = self.clean_value(row.get(mapping.get('rating', 'rating')))
                    rating = self.parse_rating(rating_str)
                    
                    # Parse genres
                    genre_str = self.clean_value(row.get(mapping.get('listed_in', 'listed_in')))
                    genres = self.parse_genres(genre_str)
                    
                    # Parse countries
                    country_str = self.clean_value(row.get(mapping.get('country', 'country')))
                    countries = self.parse_countries(country_str)
                    
                    # Create movie
                    movie = Movie(
                        title=title,
                        description=self.clean_value(row.get(mapping.get('description', 'description'))),
                        release_year=self.clean_value(row.get(mapping.get('release_year', 'release_year'))),
                        duration_minutes=duration_minutes,
                        content_type=content_type,
                        director=self.clean_value(row.get(mapping.get('director', 'director'))),
                        cast=self.clean_value(row.get(mapping.get('cast', 'cast'))),
                        rating=rating or 0.0,
                        imdb_rating=rating,
                        is_featured=False,
                        view_count=0
                    )
                    
                    # Add relationships
                    movie.genres = genres
                    movie.countries = countries
                    
                    self.db.add(movie)
                    imported_count += 1
                    
                    # Commit in batches
                    if imported_count % 100 == 0:
                        self.db.commit()
                        logger.info(f"Imported {imported_count} movies...")
                
                except Exception as e:
                    logger.error(f"Error processing row {idx}: {str(e)}")
                    self.db.rollback()
                    skipped_count += 1
                    continue
            
            # Final commit
            self.db.commit()
            
            logger.info(f"Import complete: {imported_count} imported, {skipped_count} skipped")
            return imported_count
        
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            self.db.rollback()
            raise
    
    def load_from_json(self, json_path: str) -> int:
        """Load movies from JSON file"""
        logger.info(f"Loading data from {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                data = [data]
            
            imported_count = 0
            
            for item in data:
                try:
                    title = item.get('title')
                    if not title:
                        continue
                    
                    # Check if exists
                    existing = self.db.query(Movie).filter(Movie.title == title).first()
                    if existing:
                        continue
                    
                    # Parse genres
                    genres = []
                    if 'genres' in item:
                        genre_list = item['genres'] if isinstance(item['genres'], list) else [item['genres']]
                        genres = [self.get_or_create_genre(g) for g in genre_list]
                    
                    # Parse countries
                    countries = []
                    if 'countries' in item or 'country' in item:
                        country_list = item.get('countries') or item.get('country')
                        if not isinstance(country_list, list):
                            country_list = [country_list]
                        countries = [self.get_or_create_country(c) for c in country_list]
                    
                    # Create movie
                    movie = Movie(
                        title=title,
                        description=item.get('description'),
                        release_year=item.get('release_year') or item.get('year'),
                        duration_minutes=item.get('duration_minutes') or item.get('duration'),
                        content_type=item.get('content_type') or item.get('type') or 'Movie',
                        director=item.get('director'),
                        cast=item.get('cast'),
                        rating=item.get('rating') or 0.0,
                        imdb_rating=item.get('imdb_rating'),
                        thumbnail_url=item.get('thumbnail_url') or item.get('poster'),
                        video_url=item.get('video_url'),
                        trailer_url=item.get('trailer_url'),
                        is_featured=item.get('is_featured', False),
                        view_count=item.get('view_count', 0)
                    )
                    
                    movie.genres = genres
                    movie.countries = countries
                    
                    self.db.add(movie)
                    imported_count += 1
                    
                    if imported_count % 100 == 0:
                        self.db.commit()
                        logger.info(f"Imported {imported_count} movies...")
                
                except Exception as e:
                    logger.error(f"Error processing item: {str(e)}")
                    self.db.rollback()
                    continue
            
            self.db.commit()
            logger.info(f"Import complete: {imported_count} movies imported")
            return imported_count
        
        except Exception as e:
            logger.error(f"Error loading JSON: {str(e)}")
            self.db.rollback()
            raise
    
    def close(self):
        """Close database session"""
        self.db.close()


def import_dataset(file_path: str, file_type: str = 'csv', mapping: Dict[str, str] = None):
    """
    Import dataset into database
    
    Args:
        file_path: Path to dataset file
        file_type: 'csv' or 'json'
        mapping: Column mapping for CSV files
    """
    loader = DataLoader()
    
    try:
        if file_type.lower() == 'csv':
            count = loader.load_from_csv(file_path, mapping)
        elif file_type.lower() == 'json':
            count = loader.load_from_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        logger.info(f"Successfully imported {count} movies")
        
        # Build embeddings for new movies
        logger.info("Building embeddings for imported movies...")
        from app.ai.embeddings.build_movie_embeddings import build_movie_embeddings
        build_movie_embeddings()
        
        return count
    
    finally:
        loader.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_to_db.py <dataset_file> [file_type]")
        print("Example: python load_to_db.py data/raw/netflix.csv csv")
        sys.exit(1)
    
    file_path = sys.argv[1]
    file_type = sys.argv[2] if len(sys.argv) > 2 else 'csv'
    
    # Netflix dataset column mapping
    netflix_mapping = {
        'title': 'title',
        'type': 'type',
        'description': 'description',
        'release_year': 'release_year',
        'duration': 'duration',
        'listed_in': 'listed_in',
        'country': 'country',
        'director': 'director',
        'cast': 'cast',
        'rating': 'rating'
    }
    
    import_dataset(file_path, file_type, netflix_mapping)
