#!/bin/bash

# NJShop Backend Development Startup Script
# This script sets up Docker services and Django

set -e

echo "🚀 NJShop Backend Development Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created. Please edit it with your values.${NC}"
    else
        echo -e "${RED}✗ .env.example not found!${NC}"
        exit 1
    fi
fi

# Start Docker services
echo ""
echo -e "${YELLOW}📦 Starting Docker services (PostgreSQL, Redis, Celery)...${NC}"
docker-compose up -d

# Wait for PostgreSQL to be healthy
echo ""
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
until docker exec khusi_postgres pg_isready -U khusi > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"

# Wait for Redis to be healthy
echo ""
echo -e "${YELLOW}⏳ Waiting for Redis to be ready...${NC}"
until docker exec khusi_redis redis-cli ping > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ Redis is ready${NC}"

# Check if venv exists
if [ ! -d venv ]; then
    echo ""
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo ""
echo -e "${YELLOW}📚 Installing Python dependencies...${NC}"
pip install -q uv
uv pip install -e . > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Run migrations
echo ""
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
python manage.py migrate --noinput > /dev/null 2>&1
echo -e "${GREEN}✓ Migrations applied${NC}"

# Create superuser if doesn't exist
echo ""
echo -e "${YELLOW}👤 Checking for superuser...${NC}"
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
    echo -e "${YELLOW}No superuser found. Creating one...${NC}"
    python manage.py createsuperuser --noinput || true
    echo -e "${GREEN}✓ You can create a superuser later with: python manage.py createsuperuser${NC}"
else
    echo -e "${GREEN}✓ Superuser exists${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Services running:${NC}"
echo "  📦 PostgreSQL:     localhost:5432"
echo "  🔴 Redis:          localhost:6379"
echo "  🐜 Celery Worker:  Running in Docker"
echo ""
echo -e "${YELLOW}To start the development server:${NC}"
echo ""
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo -e "${YELLOW}Then open:${NC}"
echo "  🌐 API:       http://localhost:8000"
echo "  🔐 Admin:     http://localhost:8000/admin"
echo ""
echo -e "${YELLOW}To stop Docker services:${NC}"
echo "  docker-compose down"
echo ""
