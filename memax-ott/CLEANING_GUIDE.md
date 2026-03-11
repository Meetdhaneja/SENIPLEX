# 🧹 Netflix Dataset Cleaning Guide

## What This Does

The cleaning script will:

✅ **Detect and standardize column names**
- Maps variations like 'show_title' → 'title'
- Handles different CSV formats automatically

✅ **Remove duplicates**
- Removes exact duplicate rows
- Removes duplicate titles (case-insensitive)

✅ **Clean and validate data**
- Removes extra whitespace
- Standardizes text formatting
- Validates years (1900-2030)
- Normalizes ratings
- Standardizes duration format
- Cleans genre lists

✅ **Remove invalid entries**
- Removes rows without titles
- Removes corrupted data

✅ **Standardize format**
- Consistent column order
- UTF-8 encoding
- Proper CSV formatting

---

## How to Use

### Step 1: Paste Your Data

Make sure your Netflix CSV data is in:
```
backend\app\data\raw\Netflix_dataset.csv
```

### Step 2: Clean the Dataset

**Option A: Automatic (Recommended)**
```
Double-click: CLEAN_AND_IMPORT.bat
```

This will:
1. Clean and process the dataset
2. Show statistics
3. Ask if you want to import
4. Import to database

**Option B: Manual**
```bash
cd backend
venv\Scripts\activate
python clean_netflix_dataset.py
```

### Step 3: Review Results

The script will create:
```
backend\app\data\raw\Netflix_dataset_cleaned.csv
```

You'll see statistics like:
```
==============================================================
DATASET CLEANING STATISTICS
==============================================================
Original rows:        8807
Duplicates removed:   45
Missing titles:       12
Invalid rows removed: 57
Final cleaned rows:   8750
Data retention:       99.4%
==============================================================

Column Summary:
------------------------------------------------------------
title               : 8750 / 8750 (100.0%)
type                : 8750 / 8750 (100.0%)
description         : 8745 / 8750 ( 99.9%)
release_year        : 8720 / 8750 ( 99.7%)
duration            : 8750 / 8750 (100.0%)
listed_in           : 8750 / 8750 (100.0%)
country             : 7850 / 8750 ( 89.7%)
director            : 6234 / 8750 ( 71.2%)
cast                : 7982 / 8750 ( 91.2%)
rating              : 8750 / 8750 (100.0%)
==============================================================
```

### Step 4: Import to Database

After cleaning, import the cleaned dataset:

**If you used CLEAN_AND_IMPORT.bat:**
- Just answer 'y' when prompted

**If you cleaned manually:**
```bash
python import_dataset.py app/data/raw/Netflix_dataset_cleaned.csv
```

---

## What Gets Cleaned

### Column Name Standardization

**Before:**
```csv
show_title,content_type,plot,year,runtime,genres,production_country
```

**After:**
```csv
title,type,description,release_year,duration,listed_in,country
```

### Duplicate Removal

**Before:**
```csv
title,type
"Inception","Movie"
"inception","Movie"  ← Duplicate (case-insensitive)
"Inception","Movie"  ← Exact duplicate
```

**After:**
```csv
title,type
"Inception","Movie"
```

### Duration Standardization

**Before:**
```csv
duration
"2 hours 30 minutes"
"150"
"2h 30m"
"5 Seasons"
```

**After:**
```csv
duration
"150 min"
"150 min"
"150 min"
"5 Seasons"
```

### Genre Cleaning

**Before:**
```csv
listed_in
"Action | Drama | Thriller"
"Sci-Fi; Fantasy"
"Comedy & Romance"
```

**After:**
```csv
listed_in
"Action, Drama, Thriller"
"Sci-Fi, Fantasy"
"Comedy, Romance"
```

### Rating Normalization

**Before:**
```csv
rating
"85"
"8.5/10"
"PG-13"
```

**After:**
```csv
rating
8.5
8.5
"PG-13"
```

### Text Cleaning

**Before:**
```csv
description
"  A   story   about    dreams  "
"Line 1
Line 2"
```

**After:**
```csv
description
"A story about dreams"
"Line 1 Line 2"
```

---

## Supported Input Formats

The cleaner automatically detects and handles:

### Format 1: Netflix Official (Kaggle)
```csv
show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description
```

### Format 2: Simplified
```csv
title,type,description,release_year,duration,listed_in,country,rating
```

### Format 3: Custom Columns
```csv
movie_name,content_type,plot,year,runtime,genres,production_country,score
```

**The cleaner will automatically map these to standard format!**

---

## Troubleshooting

### Error: "File not found"
**Solution:**
```bash
# Check file exists
dir backend\app\data\raw\Netflix_dataset.csv

# Make sure you pasted data into the file
```

### Error: "File is empty"
**Solution:**
1. Open `Netflix_dataset.csv` in Notepad
2. Paste your Netflix CSV data
3. Save the file
4. Run cleaner again

### Error: "UnicodeDecodeError"
**Solution:**
The cleaner tries multiple encodings automatically. If it still fails:
1. Open CSV in Notepad
2. Save As → Encoding: UTF-8
3. Run cleaner again

### Warning: "Many rows removed"
**Solution:**
- Check the statistics to see why
- Common reasons:
  - Missing titles
  - Duplicate entries
  - Corrupted data
- Review `Netflix_dataset_cleaned.csv` to verify

---

## Advanced Options

### Clean Only (Don't Import)

```bash
cd backend
venv\Scripts\activate
python clean_netflix_dataset.py
```

Then review the cleaned file before importing.

### Custom Input/Output Files

Edit `clean_netflix_dataset.py`:
```python
input_file = "app/data/raw/my_custom_file.csv"
output_file = "app/data/raw/my_custom_file_cleaned.csv"
```

### Keep Original File

The cleaner always creates a new `_cleaned.csv` file, so your original is safe!

---

## Quality Checks

The cleaner performs these checks:

✅ **Title validation**
- Must have a title
- No empty titles
- Removes extra whitespace

✅ **Year validation**
- Must be between 1900-2030
- Converts to integer
- Removes invalid years

✅ **Duration validation**
- Standardizes format
- Handles multiple formats
- Preserves "Seasons" for TV shows

✅ **Genre validation**
- Standardizes separators
- Removes empty genres
- Trims whitespace

✅ **Rating validation**
- Keeps maturity ratings (PG, R, etc.)
- Normalizes numeric ratings to 0-10
- Removes invalid ratings

---

## Example: Complete Workflow

```bash
# 1. Paste your Netflix CSV data into:
#    backend\app\data\raw\Netflix_dataset.csv

# 2. Clean and import
CLEAN_AND_IMPORT.bat

# Output:
# ========================================
# Netflix Dataset Cleaner
# ========================================
# 
# File found! Size: 2450.45 KB
# 
# ========================================
# Step 1: Cleaning and Processing Dataset
# ========================================
# 
# INFO: Loading data from app/data/raw/Netflix_dataset.csv
# INFO: Successfully loaded with utf-8 encoding
# INFO: Loaded 8807 rows with 12 columns
# INFO: Removing duplicates...
# INFO: Removed 45 duplicate entries
# INFO: Removing invalid rows...
# INFO: Removed 12 rows with missing titles
# INFO: Cleaning all fields...
# INFO: Successfully saved 8750 rows
# 
# ==============================================================
# DATASET CLEANING STATISTICS
# ==============================================================
# Original rows:        8807
# Duplicates removed:   45
# Missing titles:       12
# Invalid rows removed: 57
# Final cleaned rows:   8750
# Data retention:       99.4%
# ==============================================================
# 
# ✅ SUCCESS!
# Cleaned dataset saved to: app/data/raw/Netflix_dataset_cleaned.csv
# 
# ========================================
# Step 2: Import Cleaned Dataset
# ========================================
# 
# Import cleaned dataset to database? (y/n): y
# 
# Importing cleaned dataset...
# INFO: Imported 100 movies...
# INFO: Imported 200 movies...
# ...
# ✅ Import completed successfully!
# 📊 Total movies imported: 8750

# 3. Start application
START.bat

# 4. Visit http://localhost:3000
```

---

## Summary

**The cleaning process ensures:**

✅ No duplicates
✅ Standardized format
✅ Valid data only
✅ Consistent column names
✅ Clean text fields
✅ Proper encoding
✅ Ready for import

**Just run `CLEAN_AND_IMPORT.bat` and everything is handled automatically!**

---

**🎬 Your Netflix dataset will be perfectly cleaned and ready to use!**
