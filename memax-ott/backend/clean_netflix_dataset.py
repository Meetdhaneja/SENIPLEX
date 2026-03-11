"""
Netflix Dataset Cleaner and Processor
Cleans, validates, and prepares Netflix dataset for import
"""
import pandas as pd
import re
from pathlib import Path
from loguru import logger
import sys


class NetflixDatasetCleaner:
    """Clean and process Netflix dataset"""
    
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or input_file.replace('.csv', '_cleaned.csv')
        self.df = None
        self.stats = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'removed_rows': 0,
            'duplicates_removed': 0,
            'missing_titles': 0,
            'cleaned_fields': 0
        }
    
    def load_data(self):
        """Load CSV data"""
        logger.info(f"Loading data from {self.input_file}")
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(self.input_file, encoding=encoding)
                    logger.info(f"Successfully loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                raise Exception("Could not load file with any encoding")
            
            self.stats['original_rows'] = len(self.df)
            logger.info(f"Loaded {len(self.df)} rows with {len(self.df.columns)} columns")
            logger.info(f"Columns: {list(self.df.columns)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def detect_column_mapping(self):
        """Detect and standardize column names"""
        logger.info("Detecting column mapping...")
        
        # Common column name variations
        column_mapping = {
            'title': ['title', 'name', 'show_title', 'movie_name', 'show_name'],
            'type': ['type', 'content_type', 'category', 'show_type'],
            'description': ['description', 'plot', 'summary', 'overview', 'synopsis'],
            'release_year': ['release_year', 'year', 'release_date', 'year_released'],
            'duration': ['duration', 'runtime', 'length', 'time'],
            'listed_in': ['listed_in', 'genres', 'genre', 'categories', 'category'],
            'country': ['country', 'countries', 'production_country', 'origin'],
            'director': ['director', 'directors', 'directed_by'],
            'cast': ['cast', 'actors', 'starring', 'stars'],
            'rating': ['rating', 'maturity_rating', 'age_rating', 'content_rating'],
            'date_added': ['date_added', 'added_date', 'upload_date']
        }
        
        # Create rename mapping
        rename_map = {}
        for standard_name, variations in column_mapping.items():
            for col in self.df.columns:
                if col.lower().strip() in variations:
                    rename_map[col] = standard_name
                    break
        
        if rename_map:
            logger.info(f"Renaming columns: {rename_map}")
            self.df.rename(columns=rename_map, inplace=True)
    
    def clean_text(self, text):
        """Clean text fields"""
        if pd.isna(text) or text == '':
            return None
        
        text = str(text).strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove leading/trailing quotes if present
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        return text if text else None
    
    def clean_duration(self, duration):
        """Clean and standardize duration"""
        if pd.isna(duration):
            return None
        
        duration = str(duration).strip().lower()
        
        # Already in good format
        if 'min' in duration or 'season' in duration:
            return duration
        
        # Try to extract numbers
        numbers = re.findall(r'\d+', duration)
        if numbers:
            num = numbers[0]
            if 'hour' in duration or 'hr' in duration:
                return f"{int(num) * 60} min"
            elif 'season' in duration:
                return f"{num} Season{'s' if int(num) > 1 else ''}"
            else:
                return f"{num} min"
        
        return duration
    
    def clean_year(self, year):
        """Clean and validate release year"""
        if pd.isna(year):
            return None
        
        try:
            year = int(float(year))
            # Validate year range
            if 1900 <= year <= 2030:
                return year
        except:
            pass
        
        return None
    
    def clean_rating(self, rating):
        """Clean and normalize rating"""
        if pd.isna(rating):
            return None
        
        rating_str = str(rating).strip()
        
        # If it's a maturity rating (PG, R, etc.), return as is
        maturity_ratings = ['G', 'PG', 'PG-13', 'R', 'NC-17', 'TV-Y', 'TV-Y7', 
                           'TV-G', 'TV-PG', 'TV-14', 'TV-MA', 'NR', 'UR']
        if rating_str.upper() in maturity_ratings:
            return rating_str.upper()
        
        # Try to extract numeric rating
        try:
            rating_num = float(re.sub(r'[^\d.]', '', rating_str))
            # Normalize to 0-10 scale
            if rating_num > 10:
                rating_num = rating_num / 10
            return round(rating_num, 1)
        except:
            return None
    
    def clean_genres(self, genres):
        """Clean and standardize genres"""
        if pd.isna(genres):
            return None
        
        genres = str(genres).strip()
        
        # Standardize separators to comma
        genres = genres.replace('|', ',').replace(';', ',').replace('&', ',')
        
        # Clean each genre
        genre_list = [g.strip() for g in genres.split(',') if g.strip()]
        
        return ', '.join(genre_list) if genre_list else None
    
    def remove_duplicates(self):
        """Remove duplicate entries"""
        logger.info("Removing duplicates...")
        
        before = len(self.df)
        
        # Remove exact duplicates
        self.df.drop_duplicates(inplace=True)
        
        # Remove duplicates based on title (case-insensitive)
        if 'title' in self.df.columns:
            self.df['title_lower'] = self.df['title'].str.lower().str.strip()
            self.df.drop_duplicates(subset=['title_lower'], keep='first', inplace=True)
            self.df.drop(columns=['title_lower'], inplace=True)
        
        after = len(self.df)
        duplicates = before - after
        
        self.stats['duplicates_removed'] = duplicates
        logger.info(f"Removed {duplicates} duplicate entries")
    
    def remove_invalid_rows(self):
        """Remove rows with missing critical data"""
        logger.info("Removing invalid rows...")
        
        before = len(self.df)
        
        # Remove rows without title
        if 'title' in self.df.columns:
            missing_titles = self.df['title'].isna().sum()
            self.df = self.df[self.df['title'].notna()]
            self.stats['missing_titles'] = missing_titles
            logger.info(f"Removed {missing_titles} rows with missing titles")
        
        after = len(self.df)
        self.stats['removed_rows'] = before - after
    
    def clean_all_fields(self):
        """Clean all data fields"""
        logger.info("Cleaning all fields...")
        
        # Clean text fields
        text_fields = ['title', 'description', 'director', 'cast', 'country']
        for field in text_fields:
            if field in self.df.columns:
                self.df[field] = self.df[field].apply(self.clean_text)
                logger.info(f"Cleaned {field}")
        
        # Clean duration
        if 'duration' in self.df.columns:
            self.df['duration'] = self.df['duration'].apply(self.clean_duration)
            logger.info("Cleaned duration")
        
        # Clean year
        if 'release_year' in self.df.columns:
            self.df['release_year'] = self.df['release_year'].apply(self.clean_year)
            logger.info("Cleaned release_year")
        
        # Clean genres
        if 'listed_in' in self.df.columns:
            self.df['listed_in'] = self.df['listed_in'].apply(self.clean_genres)
            logger.info("Cleaned genres")
        
        # Clean rating
        if 'rating' in self.df.columns:
            self.df['rating'] = self.df['rating'].apply(self.clean_rating)
            logger.info("Cleaned rating")
        
        # Standardize type
        if 'type' in self.df.columns:
            self.df['type'] = self.df['type'].apply(
                lambda x: 'Movie' if str(x).lower() in ['movie', 'film'] 
                else 'TV Show' if str(x).lower() in ['tv show', 'series', 'tv series'] 
                else x
            )
            logger.info("Standardized content type")
    
    def add_missing_columns(self):
        """Add any missing standard columns"""
        standard_columns = ['title', 'type', 'description', 'release_year', 
                          'duration', 'listed_in', 'country', 'director', 
                          'cast', 'rating']
        
        for col in standard_columns:
            if col not in self.df.columns:
                self.df[col] = None
                logger.info(f"Added missing column: {col}")
    
    def reorder_columns(self):
        """Reorder columns in standard format"""
        logger.info("Reordering columns...")
        
        # Preferred column order
        column_order = ['title', 'type', 'description', 'release_year', 
                       'duration', 'listed_in', 'country', 'director', 
                       'cast', 'rating', 'date_added']
        
        # Keep only columns that exist
        existing_ordered = [col for col in column_order if col in self.df.columns]
        
        # Add any remaining columns
        remaining = [col for col in self.df.columns if col not in existing_ordered]
        
        final_order = existing_ordered + remaining
        self.df = self.df[final_order]
    
    def save_cleaned_data(self):
        """Save cleaned dataset"""
        logger.info(f"Saving cleaned data to {self.output_file}")
        
        try:
            self.df.to_csv(self.output_file, index=False, encoding='utf-8')
            self.stats['cleaned_rows'] = len(self.df)
            logger.info(f"Successfully saved {len(self.df)} rows")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return False
    
    def print_statistics(self):
        """Print cleaning statistics"""
        print("\n" + "="*60)
        print("DATASET CLEANING STATISTICS")
        print("="*60)
        print(f"Original rows:        {self.stats['original_rows']}")
        print(f"Duplicates removed:   {self.stats['duplicates_removed']}")
        print(f"Missing titles:       {self.stats['missing_titles']}")
        print(f"Invalid rows removed: {self.stats['removed_rows']}")
        print(f"Final cleaned rows:   {self.stats['cleaned_rows']}")
        print(f"Data retention:       {(self.stats['cleaned_rows']/self.stats['original_rows']*100):.1f}%")
        print("="*60)
        
        print("\nColumn Summary:")
        print("-"*60)
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            percentage = (non_null / len(self.df) * 100)
            print(f"{col:20s}: {non_null:5d} / {len(self.df):5d} ({percentage:5.1f}%)")
        print("="*60 + "\n")
    
    def process(self):
        """Run complete cleaning process"""
        logger.info("Starting dataset cleaning process...")
        
        # Load data
        if not self.load_data():
            return False
        
        # Detect and map columns
        self.detect_column_mapping()
        
        # Clean data
        self.remove_duplicates()
        self.remove_invalid_rows()
        self.clean_all_fields()
        self.add_missing_columns()
        self.reorder_columns()
        
        # Save cleaned data
        if not self.save_cleaned_data():
            return False
        
        # Print statistics
        self.print_statistics()
        
        logger.info("Dataset cleaning completed successfully!")
        return True


def main():
    """Main function"""
    print("="*60)
    print("Netflix Dataset Cleaner")
    print("="*60)
    print()
    
    # Default file path
    input_file = "app/data/raw/Netflix_dataset.csv"
    output_file = "app/data/raw/Netflix_dataset_cleaned.csv"
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"❌ Error: File not found: {input_file}")
        print("\nPlease make sure your Netflix dataset is at:")
        print(f"  {input_file}")
        return
    
    # Check if file has data
    file_size = Path(input_file).stat().st_size
    if file_size < 100:
        print(f"❌ Error: File appears to be empty or too small")
        print(f"File size: {file_size} bytes")
        print("\nPlease paste your Netflix CSV data into:")
        print(f"  {input_file}")
        return
    
    print(f"📁 Input file:  {input_file}")
    print(f"📁 Output file: {output_file}")
    print(f"📊 File size:   {file_size / 1024:.2f} KB")
    print()
    
    # Create cleaner and process
    cleaner = NetflixDatasetCleaner(input_file, output_file)
    
    if cleaner.process():
        print("\n✅ SUCCESS!")
        print(f"\nCleaned dataset saved to: {output_file}")
        print("\nNext steps:")
        print("1. Review the cleaned dataset")
        print("2. Import to database: python import_dataset.py app/data/raw/Netflix_dataset_cleaned.csv")
        print("3. Or use: IMPORT_NETFLIX.bat")
    else:
        print("\n❌ FAILED!")
        print("Check the error messages above")


if __name__ == "__main__":
    main()
