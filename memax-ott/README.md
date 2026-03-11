# MEMAX OTT Platform

🎬 **AI-Powered OTT Streaming Platform with Personalized Recommendations**

## 🌟 Features

- **🎥 Movie Streaming**: High-quality video streaming platform
- **🤖 AI Recommendations**: Personalized content suggestions using ML
- **👤 User Management**: Complete authentication and profile system
- **📊 Admin Dashboard**: Comprehensive analytics and management
- **🔍 Smart Search**: Advanced search with filters
- **📈 Analytics**: Real-time viewing statistics
- **⚡ Continue Watching**: Resume from where you left off
- **🎯 Genre & Country Filters**: Browse by preferences

## 🏗️ Architecture

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Robust relational database
- **Redis**: High-performance caching
- **SQLAlchemy**: ORM for database operations
- **Sentence Transformers**: AI-powered embeddings
- **FAISS**: Vector similarity search
- **JWT**: Secure authentication

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern styling
- **Zustand**: State management
- **Axios**: HTTP client

### AI/ML Engine
- **Content-Based Filtering**: Using movie metadata
- **Collaborative Filtering**: Based on user behavior
- **Hybrid Recommendations**: Combined approach
- **Cold Start Handling**: For new users/movies
- **Real-time Updates**: Dynamic preference learning

## 📦 Project Structure

```
memax-ott/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── ai/             # AI/ML Engine
│   │   ├── core/           # Core configurations
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry
│   └── requirements.txt
│
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Pages (App Router)
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── store/         # State management
│   └── package.json
│
├── database/              # SQL Scripts
│   ├── schema.sql
│   └── indexes.sql
│
└── docker/               # Docker Configuration
    └── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd memax-ott

# Start all services
cd docker
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your configuration

# Generate all backend files
python setup_project.py

# Initialize database
python -m app.db.init_db
python -m app.db.seed

# Run the server
python -m app.main
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Generate all frontend files
python setup_frontend.py

# Run development server
npm run dev
```

## 🔑 Default Credentials

**Admin Account:**
- Email: `admin@memax.com`
- Password: `admin123`

⚠️ **Important**: Change these credentials in production!

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

#### Movies
- `GET /api/movies` - List movies (with pagination)
- `GET /api/movies/{id}` - Get movie details
- `GET /api/movies/featured` - Featured movies
- `GET /api/movies/trending` - Trending movies
- `GET /api/movies/search` - Search movies

#### Recommendations
- `POST /api/recommendations/personalized` - Get personalized recommendations
- `GET /api/recommendations/similar/{id}` - Get similar movies
- `GET /api/recommendations/cold-start` - Cold start recommendations

#### Interactions
- `POST /api/interactions` - Record interaction
- `POST /api/interactions/progress` - Update watch progress
- `GET /api/interactions/progress` - Get continue watching

#### Admin
- `GET /api/admin/stats` - Platform statistics
- `GET /api/admin/users` - List all users

## 🎯 Features in Detail

### AI Recommendation Engine

The platform uses a sophisticated multi-stage recommendation system:

1. **Content-Based Filtering**
   - Uses Sentence Transformers (MiniLM) for text embeddings
   - Analyzes movie metadata (title, description, genres)
   - Generates semantic similarity scores

2. **Collaborative Filtering**
   - Tracks user interactions (views, likes, ratings)
   - Builds user preference profiles
   - Identifies similar users and their preferences

3. **Hybrid Approach**
   - Combines content and collaborative signals
   - Applies time decay for recent preferences
   - Ensures diversity in recommendations

4. **Cold Start Handling**
   - New users: Popular and trending content
   - New movies: Content-based similarity
   - Gradual transition to personalized recommendations

### Analytics & Tracking

- Real-time view tracking
- Watch progress monitoring
- Interaction logging
- Recommendation effectiveness metrics
- User behavior analysis

## 🛠️ Development

### Backend Development

```bash
# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/

# Run linter
flake8 app/
```

### Frontend Development

```bash
# Run linter
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

## 📊 Database Schema

The platform uses PostgreSQL with the following main tables:

- `users` - User accounts
- `movies` - Movie catalog
- `genres` - Movie genres
- `countries` - Production countries
- `watch_history` - Viewing history
- `watch_progress` - Continue watching data
- `interactions` - User-movie interactions
- `user_features` - ML user features
- `movie_embeddings` - Vector embeddings
- `recommendation_logs` - Recommendation tracking

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Rate limiting
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection

## 🚀 Deployment

### Production Checklist

- [ ] Change default admin credentials
- [ ] Update SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set up Redis with persistence
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure CDN for static assets
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/memax_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 📈 Performance Optimization

- Database indexing for common queries
- Redis caching for frequent requests
- FAISS for fast vector similarity search
- Lazy loading of movie thumbnails
- Pagination for large datasets
- Connection pooling
- Async operations where applicable

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Next.js for the powerful React framework
- Sentence Transformers for embeddings
- PostgreSQL and Redis teams

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@memax.com

## 🗺️ Roadmap

- [ ] Mobile apps (iOS/Android)
- [ ] Live streaming support
- [ ] Social features (comments, reviews)
- [ ] Watchlist and favorites
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Content upload system
- [ ] Payment integration
- [ ] Email notifications
- [ ] PWA support

---

**Built with ❤️ by the MEMAX Team**
