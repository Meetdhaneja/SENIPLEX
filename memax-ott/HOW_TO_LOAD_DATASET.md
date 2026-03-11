# 🎯 QUICK GUIDE: Load Your Own Dataset

## Step-by-Step Instructions

### Step 1: Place Your Dataset File

**Put your dataset file HERE:**
```
C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend\app\data\raw\
```

**Supported file names:**
- `netflix.csv`
- `movies.csv`
- `dataset.csv`
- `my_movies.csv`
- Any `.csv` or `.json` file

**Example:**
```
memax-ott/
└── backend/
    └── app/
        └── data/
            └── raw/
                ├── netflix.csv          ← PUT YOUR FILE HERE
                ├── movies.csv           ← OR HERE
                └── your_dataset.csv     ← OR HERE
```

---

### Step 2: Run the Import

**Option A: Automatic (Easiest)**
```bash
# Double-click this file:
IMPORT_DATA.bat
```

**Option B: Manual**
```bash
# Open Command Prompt
cd C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend

# Activate virtual environment
venv\Scripts\activate

# Run import
python import_dataset.py
```

**Option C: Specify File Directly**
```bash
cd C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend
venv\Scripts\activate
python import_dataset.py app/data/raw/YOUR_FILE.csv
```

---

## 📊 Your Dataset Format

### If you have a CSV file:

**Minimum Required Column:**
- `title` - Movie/show title

**Optional Columns (any of these):**
- `type` - "Movie" or "TV Show"
- `description` - Plot summary
- `release_year` - Year (e.g., 2020)
- `duration` - Duration (e.g., "120 min" or "2h 30m")
- `listed_in` - Genres (e.g., "Action, Drama")
- `country` - Countries (e.g., "United States, UK")
- `director` - Director name
- `cast` - Actors (e.g., "Actor1, Actor2")
- `rating` - Rating (0-10 or 0-100)

**Example CSV:**
```csv
title,type,description,release_year,duration,listed_in,country,director,cast,rating
"Inception","Movie","Dream heist",2010,"148 min","Sci-Fi, Thriller","USA","Nolan","DiCaprio",8.8
"Breaking Bad","TV Show","Chemistry teacher",2008,"5 Seasons","Drama, Crime","USA","Gilligan","Cranston",9.5
```

### If you have a JSON file:

```json
[
  {
    "title": "Inception",
    "type": "Movie",
    "description": "Dream heist",
    "release_year": 2010,
    "duration_minutes": 148,
    "genres": ["Sci-Fi", "Thriller"],
    "countries": ["USA"],
    "director": "Christopher Nolan",
    "cast": "Leonardo DiCaprio",
    "rating": 8.8
  }
]
```

---

## 🔧 If Your CSV Has Different Column Names

Create a file called `my_import.py` in the `backend` folder:

```python
from app.data.loaders.load_to_db import import_dataset

# Map YOUR column names to standard names
custom_mapping = {
    'title': 'movie_name',        # If your title column is called 'movie_name'
    'release_year': 'year',        # If your year column is called 'year'
    'description': 'plot',         # If your description is called 'plot'
    'listed_in': 'genres',         # If your genres column is called 'genres'
    'duration': 'runtime',         # If your duration is called 'runtime'
    'rating': 'score',             # If your rating is called 'score'
}

# Import with custom mapping
import_dataset('app/data/raw/YOUR_FILE.csv', 'csv', custom_mapping)
```

Then run:
```bash
cd backend
venv\Scripts\activate
python my_import.py
```

---

## 📝 Real Example

Let's say you have a file called `my_movies.csv`:

### 1. Copy file to the right location:
```
Copy: C:\Downloads\my_movies.csv
To:   C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend\app\data\raw\my_movies.csv
```

### 2. Run import:
```bash
# Double-click:
IMPORT_DATA.bat

# Or manually:
cd C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend
venv\Scripts\activate
python import_dataset.py app/data/raw/my_movies.csv
```

### 3. Wait for completion:
```
🚀 Starting import...
INFO: Read 1000 rows from CSV
INFO: Imported 100 movies...
INFO: Imported 200 movies...
...
✅ Import completed successfully!
📊 Total movies imported: 1000
```

### 4. Start the app:
```bash
# Double-click:
START.bat

# Then visit:
http://localhost:3000
```

---

## ❓ Common Questions

### Q: Where exactly do I put my file?
**A:** In this folder:
```
C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend\app\data\raw\
```

### Q: What should I name my file?
**A:** Any name works! Examples:
- `netflix.csv`
- `movies.csv`
- `my_dataset.csv`
- `films.json`

### Q: My CSV has different column names, what do I do?
**A:** Create a custom mapping (see "If Your CSV Has Different Column Names" above)

### Q: Can I import multiple datasets?
**A:** Yes! Run the import script multiple times with different files.

### Q: What if I get an error?
**A:** Check:
1. File is in `backend/app/data/raw/` folder
2. PostgreSQL is running
3. Database is initialized: `python -m app.db.init_db`
4. Virtual environment is activated

---

## 🎯 Quick Checklist

- [ ] Dataset file is in `backend/app/data/raw/` folder
- [ ] PostgreSQL is running
- [ ] Database is initialized (`python -m app.db.init_db`)
- [ ] Virtual environment is activated
- [ ] Run `IMPORT_DATA.bat` or `python import_dataset.py`

---

## 💡 Pro Tips

1. **Test with small sample first**: Create a CSV with just 10 rows to test
2. **Check your CSV**: Open in Excel/Notepad to verify format
3. **Use UTF-8 encoding**: If you have special characters
4. **One title per row**: Each row should be one movie/show

---

## 🆘 Need Help?

If you're stuck, show me:
1. First 3 lines of your CSV file
2. Column names in your CSV
3. Any error messages you see

I'll help you create the exact import command!

---

**🎬 That's it! Just put your file in `backend/app/data/raw/` and run `IMPORT_DATA.bat`**
