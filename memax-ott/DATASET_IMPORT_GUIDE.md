# 📊 Dataset Import Guide

## Quick Start

### Step 1: Prepare Your Dataset

Place your dataset file in one of these locations:
```
backend/app/data/raw/netflix.csv
backend/app/data/raw/movies.csv
backend/app/data/raw/dataset.csv
```

Or use any custom location.

### Step 2: Run Import Script

```bash
cd backend
python import_dataset.py
```

Or specify the file directly:
```bash
python import_dataset.py path/to/your/dataset.csv
```

---

## Supported Dataset Formats

### 1. CSV Format (Recommended)

**Netflix Dataset Format:**
```csv
title,type,description,release_year,duration,listed_in,country,director,cast,rating
"Movie Title","Movie","Description here",2020,"120 min","Action, Drama","United States","Director Name","Actor1, Actor2",7.5
```

**Required Columns:**
- `title` - Movie/Show title (required)

**Optional Columns:**
- `type` - "Movie" or "TV Show"
- `description` - Plot summary
- `release_year` - Year released
- `duration` - Duration (e.g., "120 min", "2h 30m")
- `listed_in` - Genres (comma-separated)
- `country` - Countries (comma-separated)
- `director` - Director name
- `cast` - Cast members (comma-separated)
- `rating` - Rating (0-10 or 0-100)

### 2. JSON Format

```json
[
  {
    "title": "Movie Title",
    "type": "Movie",
    "description": "Description here",
    "release_year": 2020,
    "duration_minutes": 120,
    "genres": ["Action", "Drama"],
    "countries": ["United States"],
    "director": "Director Name",
    "cast": "Actor1, Actor2",
    "rating": 7.5,
    "thumbnail_url": "https://...",
    "video_url": "https://..."
  }
]
```

---

## Column Mapping

If your dataset has different column names, you can create a custom mapping:

```python
# In import_dataset.py, modify the mapping:
custom_mapping = {
    'title': 'movie_name',      # Your column -> Standard name
    'type': 'content_type',
    'description': 'plot',
    'release_year': 'year',
    'duration': 'runtime',
    'listed_in': 'genres',
    'country': 'production_country',
    'director': 'directed_by',
    'cast': 'actors',
    'rating': 'imdb_score'
}
```

---

## Where to Get Datasets

### Free Movie Datasets:

1. **Netflix Dataset (Kaggle)**
   - URL: https://www.kaggle.com/datasets/shivamb/netflix-shows
   - Format: CSV
   - Size: ~8,000 titles
   - Download and place in `app/data/raw/netflix.csv`

2. **TMDB 5000 Movies**
   - URL: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata
   - Format: CSV
   - Size: ~5,000 movies

3. **IMDb Datasets**
   - URL: https://www.imdb.com/interfaces/
   - Format: TSV (can be converted to CSV)
   - Size: Millions of titles

4. **MovieLens**
   - URL: https://grouplens.org/datasets/movielens/
   - Format: CSV
   - Size: Various sizes available

---

## Example: Import Netflix Dataset

### 1. Download Dataset

```bash
# Download from Kaggle
# https://www.kaggle.com/datasets/shivamb/netflix-shows
# Save as: backend/app/data/raw/netflix.csv
```

### 2. Verify File

```bash
cd backend
head app/data/raw/netflix.csv
```

### 3. Run Import

```bash
python import_dataset.py app/data/raw/netflix.csv
```

### 4. Expected Output

```
==============================================================
MEMAX OTT - Dataset Import Tool
==============================================================

📁 Dataset: app/data/raw/netflix.csv
📊 Size: 2.45 MB
📝 Type: CSV

Start import? (y/n): y

🚀 Starting import...
------------------------------------------------------------
INFO: Loading data from app/data/raw/netflix.csv
INFO: Read 8807 rows from CSV
INFO: Imported 100 movies...
INFO: Imported 200 movies...
...
INFO: Import complete: 8807 imported, 0 skipped
INFO: Building embeddings for imported movies...
------------------------------------------------------------

✅ Import completed successfully!
📊 Total movies imported: 8807
```

---

## Custom Dataset Example

If you have your own dataset with custom columns:

**Your CSV (movies_custom.csv):**
```csv
movie_name,year,plot,genre,runtime_min,imdb_score
"Inception",2010,"Dream heist","Sci-Fi, Thriller",148,8.8
```

**Create Custom Loader:**

```python
# custom_import.py
from app.data.loaders.load_to_db import import_dataset

custom_mapping = {
    'title': 'movie_name',
    'release_year': 'year',
    'description': 'plot',
    'listed_in': 'genre',
    'duration': 'runtime_min',
    'rating': 'imdb_score'
}

import_dataset('movies_custom.csv', 'csv', custom_mapping)
```

---

## Troubleshooting

### Error: "File not found"

**Solution:**
```bash
# Check file exists
ls app/data/raw/

# Create directory if needed
mkdir -p app/data/raw

# Copy your dataset
cp ~/Downloads/netflix.csv app/data/raw/
```

### Error: "Database connection failed"

**Solution:**
```bash
# 1. Check PostgreSQL is running
# Windows: Check Services
# Linux: sudo service postgresql status

# 2. Verify .env configuration
cat .env | grep DATABASE_URL

# 3. Test connection
psql -U memax_user -d memax_db -c "SELECT 1"
```

### Error: "Table does not exist"

**Solution:**
```bash
# Initialize database
python -m app.db.init_db
python -m app.db.seed

# Then retry import
python import_dataset.py
```

### Import is Slow

**Tips:**
- Large datasets (>10,000 rows) may take several minutes
- The script commits in batches of 100 for performance
- Embedding generation happens after import
- You can skip embedding generation initially and run it later

### Duplicate Movies

The import script automatically skips movies that already exist (based on title). If you want to re-import:

```bash
# Option 1: Clear database
psql -U memax_user -d memax_db -c "TRUNCATE movies CASCADE"

# Option 2: Delete specific movies via admin panel
# Visit http://localhost:8000/admin
```

---

## Advanced Usage

### Import Multiple Datasets

```bash
# Import Netflix dataset
python import_dataset.py app/data/raw/netflix.csv

# Import TMDB dataset
python import_dataset.py app/data/raw/tmdb.csv

# Import custom dataset
python import_dataset.py app/data/raw/custom.json json
```

### Programmatic Import

```python
from app.data.loaders.load_to_db import DataLoader

loader = DataLoader()

# Import CSV
loader.load_from_csv('dataset.csv')

# Import JSON
loader.load_from_json('dataset.json')

# Close connection
loader.close()
```

### Skip Embedding Generation

If you want to import data quickly without generating embeddings:

```python
# In import_dataset.py, comment out:
# build_movie_embeddings()

# Generate embeddings later:
python -m app.ai.embeddings.build_movie_embeddings
```

---

## Post-Import Steps

### 1. Verify Import

```bash
# Check movie count
psql -U memax_user -d memax_db -c "SELECT COUNT(*) FROM movies"

# Check genres
psql -U memax_user -d memax_db -c "SELECT * FROM genres"

# Check sample movies
psql -U memax_user -d memax_db -c "SELECT title, rating FROM movies LIMIT 10"
```

### 2. Build Embeddings (if skipped)

```bash
python -m app.ai.embeddings.build_movie_embeddings
```

### 3. Set Featured Movies

```sql
-- Mark top-rated movies as featured
UPDATE movies 
SET is_featured = true 
WHERE rating >= 8.0 
LIMIT 20;
```

### 4. Start Application

```bash
# Backend
python -m app.main

# Frontend (new terminal)
cd ../frontend
npm run dev
```

### 5. Browse Movies

Visit http://localhost:3000 and you should see your imported movies!

---

## Dataset Format Reference

### Supported Duration Formats
- `"120 min"` → 120 minutes
- `"2h 30m"` → 150 minutes
- `"90"` → 90 minutes
- `"1 Season"` → null (for TV shows)

### Supported Rating Formats
- `"8.5"` → 8.5
- `"8.5/10"` → 8.5
- `"85"` → 8.5 (auto-normalized)

### Supported Genre Separators
- Comma: `"Action, Drama, Thriller"`
- Pipe: `"Action | Drama | Thriller"`
- Semicolon: `"Action; Drama; Thriller"`
- Ampersand: `"Action & Drama & Thriller"`

### Supported Country Separators
- Comma: `"United States, United Kingdom"`
- Pipe: `"United States | United Kingdom"`

---

## Sample Datasets Included

The project includes sample data generators:

```bash
# Generate sample movies
python -m app.db.seed

# This creates:
# - Admin user
# - 15 genres
# - 15 countries
# - Sample movies (if you add them to seed.py)
```

---

## Need Help?

1. Check logs for detailed error messages
2. Verify your dataset format matches examples above
3. Test with a small sample (first 10 rows) before importing full dataset
4. Check the main README.md for database setup instructions

---

**Happy Importing! 🎬**
