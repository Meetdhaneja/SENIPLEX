# MEMAX OTT Platform - Installation Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1.  **Python 3.9 or higher**
    *   Download from: <https://www.python.org/downloads/>
    *   During installation, check "Add Python to PATH"
    *   Verify: `python --version`

2.  **Node.js 18 or higher**
    *   Download from: <https://nodejs.org/>
    *   Verify: `node --version` and `npm --version`

3.  **PostgreSQL 14 or higher**
    *   Download from: <https://www.postgresql.org/download/>
    *   Remember your postgres password during installation
    *   Verify: `psql --version`

4.  **Redis 6 or higher**
    *   Windows: Download from <https://github.com/microsoftarchive/redis/releases>
    *   Or use Docker: `docker run -d -p 6379:6379 redis:7-alpine`
    *   Verify: `redis-cli ping` (should return PONG)

### Optional (Recommended)

5.  **Docker Desktop** (for containerized deployment)
    *   Download from: <https://www.docker.com/products/docker-desktop/>

6.  **Git** (for version control)
    *   Download from: <https://git-scm.com/downloads>

## 🚀 Installation Methods

### Method 1: Automated Setup (Recommended for Windows)

1.  **Navigate to project directory**
    ```bash
    cd C:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott
    ```

2.  **Run setup script**
    ```bash
    SETUP.bat
    ```

3.  **Follow the on-screen instructions**

### Method 2: Manual Setup (All Platforms)

#### Step 1: Setup PostgreSQL Database

1.  **Create database and user**
    ```bash
    # Open PostgreSQL command line
    psql -U postgres
    
    # Create database
    CREATE DATABASE memax_db;
    
    # Create user
    CREATE USER memax_user WITH PASSWORD 'memax_password';
    
    # Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE memax_db TO memax_user;
    
    # Exit
    \q
    ```

2.  **Run schema scripts**
    ```bash
    psql -U memax_user -d memax_db -f database/schema.sql
    psql -U memax_user -d memax_db -f database/indexes.sql
    ```

#### Step 2: Setup Backend

1.  **Navigate to backend directory**
    ```bash
    cd backend
    ```

2.  **Create virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    
    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment**
    ```bash
    # Copy example env file
    copy .env.example .env    # Windows
    cp .env.example .env      # Linux/Mac
    
    # Edit .env file with your settings
    # Update DATABASE_URL if needed
    ```

5.  **Initialize database**
    ```bash
    python -m app.db.init_db
    python -m app.db.seed
    ```

6.  **Test backend**
    ```bash
    python -m app.main
    ```
    *   Should start on <http://localhost:8000>
    *   Visit <http://localhost:8000/docs> for API documentation

#### Step 3: Setup Frontend

1.  **Open new terminal and navigate to frontend**
    ```bash
    cd frontend
    ```

2.  **Install dependencies**
    ```bash
    npm install
    ```

3.  **Configure environment**
    ```bash
    # .env.local should already exist
    # Verify it contains:
    # NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

4.  **Test frontend**
    ```bash
    npm run dev
    ```
    *   Should start on <http://localhost:3000>

### Method 3: Docker Setup (Easiest)

1.  **Ensure Docker Desktop is running**

2.  **Navigate to docker directory**
    ```bash
    cd docker
    ```

3.  **Start all services**
    ```bash
    docker-compose up -d
    ```

4.  **Check status**
    ```bash
    docker-compose ps
    ```

5.  **View logs**
    ```bash
    docker-compose logs -f
    ```

6.  **Stop services**
    ```bash
    docker-compose down
    ```

## 🔧 Configuration

### Backend Configuration (backend/.env)

```env
# Application
APP_NAME=MEMAX OTT
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://memax_user:memax_password@localhost:5432/memax_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@memax.com

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend Configuration (frontend/.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## ✅ Verification Steps

### 1. Check Backend

```bash
# In backend directory with venv activated
python -m app.main
```

**Expected output:**
```text
INFO: Starting MEMAX OTT v1.0.0
INFO: Environment: development
INFO: Database initialized successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Test endpoints:**
*   <http://localhost:8000> - Should return welcome message
*   <http://localhost:8000/health> - Should return {"status": "healthy"}
*   <http://localhost:8000/docs> - Should show Swagger UI

### 2. Check Frontend

```bash
# In frontend directory
npm run dev
```

**Expected output:**
```text
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Test pages:**
*   <http://localhost:3000> - Home page
*   <http://localhost:3000/login> - Login page
*   <http://localhost:3000/signup> - Signup page

### 3. Check Database

```bash
psql -U memax_user -d memax_db -c "\dt"
```

**Expected tables:**
*   users
*   movies
*   genres
*   countries
*   watch_history
*   watch_progress
*   interactions
*   user_features
*   movie_embeddings
*   recommendation_logs

### 4. Check Redis

```bash
redis-cli ping
```

**Expected output:** `PONG`

## 🎯 First Run Checklist

*   [ ] PostgreSQL is running
*   [ ] Redis is running
*   [ ] Backend virtual environment is activated
*   [ ] Backend dependencies are installed
*   [ ] Database is initialized and seeded
*   [ ] Backend .env file is configured
*   [ ] Backend server starts without errors
*   [ ] Frontend dependencies are installed
*   [ ] Frontend .env.local is configured
*   [ ] Frontend server starts without errors
*   [ ] Can access frontend at <http://localhost:3000>
*   [ ] Can access backend at <http://localhost:8000>
*   [ ] Can access API docs at <http://localhost:8000/docs>

## 🔐 Default Login

After setup, you can login with:

**Admin Account:**
*   Email: `admin@memax.com`
*   Password: `admin123`

**⚠️ Important:** Change this password immediately in production!

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError`
```bash
# Solution: Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** Database connection error
```bash
# Solution: Check PostgreSQL is running
# Windows: Check Services
# Linux/Mac: sudo service postgresql status

# Verify connection string in .env
DATABASE_URL=postgresql://memax_user:memax_password@localhost:5432/memax_db
```

**Problem:** Redis connection error
```bash
# Solution: Start Redis
# Windows: Start redis-server.exe
# Linux/Mac: redis-server
# Docker: docker run -d -p 6379:6379 redis:7-alpine
```

### Frontend Issues

**Problem:** `npm install` fails
```bash
# Solution: Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem:** API connection error
```bash
# Solution: Verify backend is running
# Check .env.local has correct API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Issues

**Problem:** Tables not created
```bash
# Solution: Run initialization scripts
python -m app.db.init_db
python -m app.db.seed
```

**Problem:** Permission denied
```bash
# Solution: Grant proper permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE memax_db TO memax_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO memax_user;
```

## 📞 Getting Help

If you encounter issues:

1.  Check the logs:
    *   Backend: Terminal output
    *   Frontend: Browser console (F12)
    *   Database: PostgreSQL logs

2.  Verify all prerequisites are installed

3.  Ensure all services are running

4.  Check configuration files (.env, .env.local)

5.  Review the PROJECT_SUMMARY.md for feature details

## 🎉 Success!

If everything is working:
*   ✅ Backend running on <http://localhost:8000>
*   ✅ Frontend running on <http://localhost:3000>
*   ✅ Can login with admin credentials
*   ✅ Can browse the platform

**You're ready to start using MEMAX OTT Platform!**

## 📚 Next Steps

1.  **Explore the platform**
    *   Browse movies
    *   Test recommendations
    *   Try the admin dashboard

2.  **Add content**
    *   Use the admin panel to add movies
    *   Or import from a dataset

3.  **Customize**
    *   Update branding
    *   Modify color scheme
    *   Add features

4.  **Deploy**
    *   Follow deployment guide in README.md
    *   Set up production environment
    *   Configure domain and SSL

---

**Need more help?** Check README.md and PROJECT_SUMMARY.md for detailed documentation.
