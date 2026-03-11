# 🎬 How to Import Your Netflix Dataset

## ✅ Good News!

Your file is already in the **correct location**:
```
C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend\app\data\raw\Netflix_dataset.csv
```

---

## 📋 Step-by-Step Instructions

### Step 1: Add Your CSV Data

**Your file is currently empty.** You need to copy your Netflix CSV data into it.

**Option A: Copy from another file**
```
1. Find your Netflix CSV file on your PC
2. Open it (right-click → Open with → Notepad or Excel)
3. Copy ALL the content (Ctrl+A, then Ctrl+C)
4. Open: backend\app\data\raw\Netflix_dataset.csv
5. Paste the content (Ctrl+V)
6. Save the file (Ctrl+S)
```

**Option B: Replace the file**
```
1. Find your Netflix CSV file on your PC (e.g., Downloads\netflix_titles.csv)
2. Copy it
3. Paste and replace at:
   C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\backend\app\data\raw\Netflix_dataset.csv
```

---

### Step 2: Verify Your CSV Format

Your CSV should look like this:

**First line (headers):**
```csv
show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description
```

**Data lines (example):**
```csv
s1,Movie,Dick Johnson Is Dead,Kirsten Johnson,,United States,"September 25, 2021",2020,PG-13,90 min,"Documentaries","As her father nears the end of his life..."
s2,TV Show,Blood & Water,,,South Africa,"September 24, 2021",2021,TV-MA,2 Seasons,"International TV Shows, TV Dramas, TV Mysteries","After crossing paths..."
```

**OR simpler format:**
```csv
title,type,description,release_year,duration,listed_in,country,director,cast,rating
"Inception","Movie","Dream heist",2010,"148 min","Sci-Fi, Thriller","USA","Nolan","DiCaprio",8.8
```

---

### Step 3: Import the Dataset

**Method 1: Use the dedicated script (Easiest)**
```
Double-click: IMPORT_NETFLIX.bat
```

**Method 2: Manual command**
```bash
cd backend
venv\Scripts\activate
python import_dataset.py app/data/raw/Netflix_dataset.csv
```

**Method 3: Use general import script**
```
Double-click: IMPORT_DATA.bat
(Then select Netflix_dataset.csv when prompted)
```

---

### Step 4: Wait for Import

You'll see output like:
```
🚀 Starting import...
------------------------------------------------------------
INFO: Loading data from app/data/raw/Netflix_dataset.csv
INFO: Read 8807 rows from CSV
INFO: Loaded 15 genres and 15 countries
INFO: Imported 100 movies...
INFO: Imported 200 movies...
INFO: Imported 500 movies...
...
INFO: Import complete: 8807 imported, 0 skipped
INFO: Building embeddings for imported movies...
------------------------------------------------------------

✅ Import completed successfully!
📊 Total movies imported: 8807
```

---

### Step 5: Start the Application

```
Double-click: START.bat
```

Then visit: **http://localhost:3000**

---

## 🔧 If Your CSV Has Different Column Names

If your Netflix CSV has different column names, create this file:

**File: `backend/import_netflix_custom.py`**
```python
from app.data.loaders.load_to_db import import_dataset

# Map your column names to standard names
netflix_mapping = {
    'title': 'title',              # or 'show_title' or 'name'
    'type': 'type',                # or 'content_type'
    'description': 'description',  # or 'plot' or 'summary'
    'release_year': 'release_year',# or 'year'
    'duration': 'duration',        # or 'runtime'
    'listed_in': 'listed_in',      # or 'genres' or 'categories'
    'country': 'country',          # or 'countries'
    'director': 'director',
    'cast': 'cast',                # or 'actors'
    'rating': 'rating'             # or 'score' or 'imdb_rating'
}

# Import with custom mapping
import_dataset('app/data/raw/Netflix_dataset.csv', 'csv', netflix_mapping)
```

Then run:
```bash
cd backend
venv\Scripts\activate
python import_netflix_custom.py
```

---

## 📊 Common Netflix CSV Formats

### Format 1: Official Netflix Dataset (Kaggle)
```csv
show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description
s1,Movie,Dick Johnson Is Dead,Kirsten Johnson,,United States,"September 25, 2021",2020,PG-13,90 min,"Documentaries","Description here"
```

### Format 2: Simplified Format
```csv
title,type,description,release_year,duration,listed_in,country,rating
"Inception","Movie","Dream heist",2010,"148 min","Sci-Fi, Thriller","USA",8.8
```

### Format 3: Minimal Format (works too!)
```csv
title,type,listed_in
"Inception","Movie","Sci-Fi, Thriller"
"Breaking Bad","TV Show","Drama, Crime"
```

---

## ❓ Troubleshooting

### Problem: "File is empty"
**Solution:**
1. Open `Netflix_dataset.csv` in Notepad
2. Check if it has data
3. If empty, copy your Netflix data into it
4. Save and try again

### Problem: "No such file or directory"
**Solution:**
```bash
# Make sure file is in the right place
dir backend\app\data\raw\Netflix_dataset.csv

# Should show the file with size > 0 bytes
```

### Problem: "Column not found"
**Solution:**
1. Open your CSV in Notepad
2. Look at the first line (column names)
3. Create custom mapping (see section above)

### Problem: Import is slow
**Solution:**
- This is normal for large datasets
- 8,000 movies takes ~5-10 minutes
- Be patient, it's working!

---

## 🎯 Quick Checklist

- [ ] Netflix_dataset.csv is in `backend/app/data/raw/`
- [ ] File has data (not empty)
- [ ] First line has column headers
- [ ] PostgreSQL is running
- [ ] Database is initialized (`python -m app.db.init_db`)
- [ ] Run `IMPORT_NETFLIX.bat`

---

## 📝 Example: Complete Workflow

```bash
# 1. Check your file has data
notepad backend\app\data\raw\Netflix_dataset.csv

# 2. If empty, copy your Netflix CSV data into it and save

# 3. Import the data
IMPORT_NETFLIX.bat

# 4. Wait for completion (5-10 minutes for large files)

# 5. Start the application
START.bat

# 6. Browse your movies
# Visit: http://localhost:3000
```

---

## 🌐 Where to Get Netflix Dataset

If you don't have a Netflix dataset yet:

**Kaggle - Netflix Shows Dataset** (Recommended)
1. Visit: https://www.kaggle.com/datasets/shivamb/netflix-shows
2. Click "Download" (you may need to create a free Kaggle account)
3. Extract `netflix_titles.csv`
4. Copy content to `backend/app/data/raw/Netflix_dataset.csv`
5. Run `IMPORT_NETFLIX.bat`

---

## ✅ After Import

### Check Import Success
```bash
# Count movies
psql -U memax_user -d memax_db -c "SELECT COUNT(*) FROM movies"

# View sample
psql -U memax_user -d memax_db -c "SELECT title, rating FROM movies LIMIT 10"

# Check genres
psql -U memax_user -d memax_db -c "SELECT name FROM genres"
```

### Start Using Your Platform
```bash
# Start servers
START.bat

# Visit
http://localhost:3000

# Login
Email: admin@memax.com
Password: admin123
```

---

## 🎬 Summary

**Your file location is perfect!** Just:
1. ✅ Add your CSV data to `Netflix_dataset.csv`
2. ✅ Run `IMPORT_NETFLIX.bat`
3. ✅ Wait for import to complete
4. ✅ Run `START.bat`
5. ✅ Enjoy your movies!

---

**Need help? Show me the first 3 lines of your CSV and I'll help you import it!**
