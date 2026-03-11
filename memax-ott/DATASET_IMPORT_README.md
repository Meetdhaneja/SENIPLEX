# 🎬 MEMAX OTT - Dataset Import Summary

## ✅ What Was Created

I've added a complete dataset import system to your MEMAX OTT platform:

### 📁 New Files Created

1. **`backend/app/data/loaders/load_to_db.py`** (400+ lines)
   - Comprehensive data loader class
   - Supports CSV and JSON formats
   - Automatic genre/country creation
   - Smart parsing for duration, ratings, genres
   - Batch processing for performance
   - Error handling and logging

2. **`backend/import_dataset.py`** (150+ lines)
   - User-friendly import script
   - Interactive prompts
   - Auto-detection of datasets
   - Progress tracking
   - Error messages and troubleshooting

3. **`DATASET_IMPORT_GUIDE.md`** (Comprehensive guide)
   - Step-by-step instructions
   - Dataset format examples
   - Troubleshooting section
   - Where to get datasets
   - Custom mapping examples

4. **`IMPORT_DATA.bat`** (Windows script)
   - One-click import tool
   - Auto-detects datasets
   - Activates virtual environment

5. **`backend/app/data/raw/.gitkeep`**
   - Placeholder for dataset directory

---

## 🚀 How to Import Your Dataset

### Method 1: Quick Import (Easiest)

```bash
# 1. Place your dataset in backend/app/data/raw/
# Example: backend/app/data/raw/netflix.csv

# 2. Run the import script
IMPORT_DATA.bat
```

### Method 2: Manual Import

```bash
cd backend
python import_dataset.py
# Follow the interactive prompts
```

### Method 3: Specify File Directly

```bash
cd backend
python import_dataset.py path/to/your/dataset.csv
```

---

## 📊 Supported Dataset Formats

### Netflix Dataset (CSV)
```csv
title,type,description,release_year,duration,listed_in,country,director,cast,rating
"Inception","Movie","Dream heist",2010,"148 min","Sci-Fi, Thriller","USA","Nolan","DiCaprio",8.8
```

### Custom JSON
```json
[
  {
    "title": "Movie Title",
    "type": "Movie",
    "description": "Description",
    "release_year": 2020,
    "duration_minutes": 120,
    "genres": ["Action", "Drama"],
    "rating": 7.5
  }
]
```

---

## 🌐 Where to Get Datasets

### Recommended: Netflix Dataset (Kaggle)

1. **Visit**: https://www.kaggle.com/datasets/shivamb/netflix-shows
2. **Download**: netflix_titles.csv (~8,000 titles)
3. **Save to**: `backend/app/data/raw/netflix.csv`
4. **Import**: Run `IMPORT_DATA.bat`

### Other Options:

- **TMDB 5000 Movies**: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata
- **IMDb Datasets**: https://www.imdb.com/interfaces/
- **MovieLens**: https://grouplens.org/datasets/movielens/

---

## ✨ Features

### Smart Parsing
- ✅ Handles multiple duration formats ("120 min", "2h 30m")
- ✅ Normalizes ratings (0-10 scale)
- ✅ Parses comma/pipe/semicolon separated genres
- ✅ Auto-creates genres and countries
- ✅ Skips duplicates

### Performance
- ✅ Batch commits (100 movies at a time)
- ✅ Progress logging
- ✅ Memory efficient

### Error Handling
- ✅ Validates data before import
- ✅ Skips invalid rows
- ✅ Detailed error messages
- ✅ Rollback on failure

### Post-Import
- ✅ Automatically builds AI embeddings
- ✅ Ready for recommendations

---

## 📝 Example Usage

### Import Netflix Dataset

```bash
# 1. Download dataset from Kaggle
# Save as: backend/app/data/raw/netflix.csv

# 2. Run import
cd backend
python import_dataset.py app/data/raw/netflix.csv

# Expected output:
# 🚀 Starting import...
# INFO: Read 8807 rows from CSV
# INFO: Imported 100 movies...
# INFO: Imported 200 movies...
# ...
# ✅ Import completed successfully!
# 📊 Total movies imported: 8807
```

### Import Custom Dataset

```python
# If your CSV has different column names
from app.data.loaders.load_to_db import import_dataset

custom_mapping = {
    'title': 'movie_name',
    'release_year': 'year',
    'listed_in': 'genres'
}

import_dataset('my_movies.csv', 'csv', custom_mapping)
```

---

## 🔧 Troubleshooting

### "File not found"
```bash
# Check file exists
ls backend/app/data/raw/

# Create directory
mkdir backend/app/data/raw

# Copy dataset
cp ~/Downloads/netflix.csv backend/app/data/raw/
```

### "Database connection failed"
```bash
# 1. Start PostgreSQL
# 2. Initialize database
cd backend
python -m app.db.init_db
python -m app.db.seed
```

### "Table does not exist"
```bash
# Initialize database first
python -m app.db.init_db
```

---

## 📊 After Import

### 1. Verify Import
```bash
# Check movie count
psql -U memax_user -d memax_db -c "SELECT COUNT(*) FROM movies"
```

### 2. Start Application
```bash
# Backend
cd backend
python -m app.main

# Frontend (new terminal)
cd frontend
npm run dev
```

### 3. Browse Movies
Visit http://localhost:3000 and see your imported movies!

---

## 📚 Documentation

- **Full Guide**: `DATASET_IMPORT_GUIDE.md`
- **Data Loader Code**: `backend/app/data/loaders/load_to_db.py`
- **Import Script**: `backend/import_dataset.py`

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Import dataset | `IMPORT_DATA.bat` |
| Import specific file | `python import_dataset.py file.csv` |
| Import JSON | `python import_dataset.py file.json` |
| Check imports | `psql -U memax_user -d memax_db -c "SELECT COUNT(*) FROM movies"` |
| Build embeddings | `python -m app.ai.embeddings.build_movie_embeddings` |

---

## ✅ Summary

You now have:
- ✅ Complete dataset import system
- ✅ Support for CSV and JSON
- ✅ Smart data parsing
- ✅ Automatic genre/country creation
- ✅ Error handling
- ✅ Interactive import tool
- ✅ Comprehensive documentation
- ✅ One-click import script

**Just place your dataset in `backend/app/data/raw/` and run `IMPORT_DATA.bat`!**

---

**🎬 Ready to import your movies!**
