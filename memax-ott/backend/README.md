# MEMAX OTT Platform

AI-Powered OTT Platform with Personalized Recommendations

## Features

- 🎬 Movie Streaming Platform
- 🤖 AI-Powered Recommendations
- 👤 User Authentication & Profiles
- 📊 Admin Dashboard
- 🔍 Advanced Search
- 📈 Analytics & Insights
- ⚡ Real-time Progress Tracking

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Sentence Transformers
- FAISS

### Frontend
- Next.js
- TypeScript
- TailwindCSS

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python -m app.db.init_db
python -m app.db.seed
python -m app.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Admin Credentials

- Email: admin@memax.com
- Password: admin123

**⚠️ Change these in production!**

## License

MIT
