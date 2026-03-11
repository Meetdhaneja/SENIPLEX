#!/bin/bash
# =============================================
# MEMAX OTT - Production Deployment Script
# Run this on your VPS/Cloud server to deploy
# Usage: bash deploy.sh
# =============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "=========================================================="
echo "        🚀 MEMAX OTT - One-Click Deployment Script"
echo "=========================================================="
echo -e "${NC}"

# ─── Step 1: Check .env.production exists ─────────────────────────
if [ ! -f ".env.production" ]; then
  echo -e "${YELLOW}[INFO] .env.production not found. Creating from example...${NC}"
  cp .env.production.example .env.production
  echo -e "${RED}[ACTION REQUIRED] Edit .env.production with your real credentials before continuing.${NC}"
  echo "Open it with: nano .env.production"
  exit 1
fi

echo -e "${GREEN}[OK] .env.production found.${NC}"

# ─── Step 2: Check Docker is running ──────────────────────────────
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}[ERROR] Docker is not running. Start Docker Desktop and try again.${NC}"
  exit 1
fi
echo -e "${GREEN}[OK] Docker is running.${NC}"

# ─── Step 3: Build production images ──────────────────────────────
echo ""
echo -e "${CYAN}[BUILD] Building all Docker images (this may take a few minutes)...${NC}"

cd docker
docker compose --env-file ../.env.production build --no-cache

# ─── Step 4: Start all services ─────────────────────────────────
echo ""
echo -e "${CYAN}[START] Launching all services (postgres, redis, backend, celery, frontend, nginx)...${NC}"
docker compose --env-file ../.env.production up -d

# ─── Step 5: Wait for services to be healthy ──────────────────────
echo ""
echo -e "${CYAN}[WAIT] Waiting 15 seconds for services to initialize...${NC}"
sleep 15

# ─── Step 6: Show status ──────────────────────────────────────────
echo ""
echo -e "${CYAN}[STATUS] Current container status:${NC}"
docker compose ps

# ─── Done! ────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}"
echo "=========================================================="
echo "   ✅ MEMAX OTT is now LIVE!"
echo "=========================================================="
echo ""
echo "  Frontend:    http://localhost (via Nginx)"
echo "  Backend API: http://localhost/api"
echo "  API Docs:    http://localhost/docs"
echo "  Admin Panel: http://localhost/admin"
echo ""
echo "  To view logs:      docker compose logs -f"
echo "  To stop all:       docker compose down"
echo "  To restart:        docker compose restart"
echo -e "${NC}"
