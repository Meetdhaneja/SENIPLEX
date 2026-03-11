# 🚀 MEMAX OTT - Full System Complete

The MEMAX OTT Platform has been fully developed, integrated, and deployed locally.

## ✅ Project Status
- **Backend**: Python/FastAPI Server running on port 8000.
- **Frontend**: Cyberpunk UI (Static HTML/JS) served by the backend.
- **Database**: PostgreSQL (Netflix DB) populated with **8,798 movies**.
- **AI Engine**: Recommendation system active and integrated.
- **Authentication**: Fully functional Login & Signup system.

---

## 🖥️ How to Run Everything

**Double-click the `START_EVERYTHING.bat` file on your desktop.**

This single script will:
1.  Verify your Python installation.
2.  Start the **Backend API Server** (Wait for "Uvicorn running...").
3.  Initialize the **AI Recommendation Engine**.
4.  Launch the **Cyberpunk Frontend Website** in your browser.

---

## 📂 System Architecture

### 1. Backend (`/backend`)
- **Framework**: FastAPI (High-performance API)
- **Database**: SQLAlchemy + PostgreSQL
- **AI Models**: 
  - `ContentBasedFiltering`: TF-IDF/Cosine Similarity (matrix created).
  - `CollaborativeFiltering`: User-Item Interaction.
- **Data Loaders**: `app/data/loaders` handles CSV -> DB pipeline.

### 2. Frontend (`/backend/app/static`)
- **Theme**: Cyberpunk (Violet/Black/Neon).
- **Core Pages**:
  - `index.html`: Dashboard with Trending/New Releases.
  - `login.html`: Secure authentication.
  - `signup.html`: Create new accounts.
- **State Management**: Token-based auth stored in `localStorage`.
- **API Connection**: `app.js` handles data fetching from `/api`.

### 3. Database (`PostgreSQL`)
- **Movies**: 8,798 records loaded from `Netflix_dataset_cleaned.csv`.
- **Users**: Authentication tables seeded.
- **Features**: User embeddings and watch history.

---

## 🛠️ Troubleshooting

**Issue: "Site can't be reached"**
- Ensure the backend window is running (shows logs).
- Check if PostgreSQL service is active.
- Run `START_BACKEND.bat` manually if the all-in-one script fails.

**Issue: Movies not showing**
- Check backend logs for database errors.
- Confirm `run_import_silent.py` finished successfully (count should be ~8800).

---

## 🔗 Access Points
- **Website UI:** [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database:** Connect via PGAdmin (User: `memax_user`, DB: `memax_db`).
