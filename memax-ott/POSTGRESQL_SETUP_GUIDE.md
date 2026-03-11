# PostgreSQL Database Connection Guide 🐘

## Step-by-Step Setup for PostgreSQL Connection

### Prerequisites ✅

1. **PostgreSQL Installed** - Make sure PostgreSQL is installed on your system
2. **PostgreSQL Running** - Ensure the PostgreSQL service is running
3. **Database Created** - You need a database created for the application

---

## Step 1: Install PostgreSQL Driver

The backend needs `psycopg2` to connect to PostgreSQL.

```bash
cd backend
pip install psycopg2-binary
```

**Or** add to `requirements.txt` and install:
```bash
pip install -r requirements.txt
```

---

## Step 2: Create PostgreSQL Database

### Option A: Using pgAdmin (GUI)
1. Open pgAdmin
2. Right-click on "Databases" → Create → Database
3. Name: `memax_db`
4. Owner: `postgres` (or your user)
5. Click "Save"

### Option B: Using psql (Command Line)
```bash
# Open psql
psql -U postgres

# Create database
CREATE DATABASE memax_db;

# Create user (optional)
CREATE USER memax_user WITH PASSWORD 'memax_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE memax_db TO memax_user;

# Exit
\q
```

---

## Step 3: Configure Database Connection

### Create `.env` File

Create a file named `.env` in the `backend` directory:

**Location**: `backend/.env`

```env
# Database Configuration
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME

# Example with default PostgreSQL:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/memax_db

# Example with custom user:
# DATABASE_URL=postgresql://memax_user:memax_password@localhost:5432/memax_db

# Application Settings
APP_NAME=MEMAX OTT
DEBUG=True
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars-long

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@memax.com
```

### Replace These Values:
- **USERNAME**: Your PostgreSQL username (default: `postgres`)
- **PASSWORD**: Your PostgreSQL password
- **HOST**: Database host (default: `localhost`)
- **PORT**: PostgreSQL port (default: `5432`)
- **DATABASE_NAME**: Your database name (e.g., `memax_db`)

---

## Step 4: Verify Connection

Test the database connection:

```bash
cd backend
python -c "from app.db.session import engine; engine.connect(); print('✅ Database connected successfully!')"
```

**Expected Output:**
```
✅ Database connected successfully!
```

**If you get an error:**
- Check PostgreSQL is running
- Verify username/password
- Ensure database exists
- Check port number (default: 5432)

---

## Step 5: Create Database Tables

Run database migrations to create all tables:

```bash
cd backend
python -c "from app.db.init_db import init_db; init_db(); print('✅ Database tables created!')"
```

This will create all necessary tables:
- users
- movies
- genres
- interactions
- watch_history
- movie_embeddings
- user_embeddings
- recommendation_logs
- etc.

---

## Step 6: Verify Tables Created

Check if tables were created:

```bash
# Using psql
psql -U postgres -d memax_db -c "\dt"

# Or using Python
python -c "from app.db.session import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('Tables:', inspector.get_table_names())"
```

---

## Step 7: Import Sample Data (Optional)

If you have a dataset to import:

```bash
cd memax-ott
.\IMPORT_DATA.bat
```

Or manually:
```bash
cd backend
python import_dataset.py
```

---

## Common Connection String Formats

### Local PostgreSQL (Default User)
```
postgresql://postgres:your_password@localhost:5432/memax_db
```

### Local PostgreSQL (Custom User)
```
postgresql://memax_user:memax_password@localhost:5432/memax_db
```

### Remote PostgreSQL
```
postgresql://username:password@remote-host.com:5432/memax_db
```

### PostgreSQL with SSL
```
postgresql://username:password@host:5432/memax_db?sslmode=require
```

### Cloud PostgreSQL (e.g., Heroku)
```
postgresql://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/dbname
```

---

## Troubleshooting

### Error: "password authentication failed"
**Solution**: Check your PostgreSQL password
```bash
# Reset password in psql
psql -U postgres
ALTER USER postgres PASSWORD 'new_password';
```

### Error: "database does not exist"
**Solution**: Create the database
```bash
psql -U postgres
CREATE DATABASE memax_db;
```

### Error: "could not connect to server"
**Solution**: Start PostgreSQL service
```bash
# Windows
net start postgresql-x64-14

# Or check services.msc for PostgreSQL service
```

### Error: "peer authentication failed"
**Solution**: Edit `pg_hba.conf` to use `md5` instead of `peer`
```
# Find pg_hba.conf (usually in PostgreSQL data directory)
# Change:
local   all   all   peer
# To:
local   all   all   md5
```

### Error: "port 5432 already in use"
**Solution**: PostgreSQL is already running, or another service is using port 5432

---

## Quick Setup Script

I'll create a setup script for you in the next step that automates this process.

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `DB_ECHO` | Log SQL queries (debug) | `False` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-min-32-chars` |
| `DEBUG` | Debug mode | `True` |
| `ENVIRONMENT` | Environment name | `development` |

---

## Next Steps After Connection

1. ✅ Database connected
2. ✅ Tables created
3. ⏳ Import data (optional)
4. ⏳ Restart backend server
5. ⏳ Test API endpoints

---

**Status**: Ready for PostgreSQL connection setup! 🚀
