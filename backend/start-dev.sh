#!/bin/bash

# NJShop Backend - One Command Full Setup
# Just run this once, everything will be ready!

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║  🚀 NJShop Backend - Full Setup         ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Create .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
fi

# Create venv
if [ ! -d venv ]; then
    echo -e "${YELLOW}🐍 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📚 Installing dependencies...${NC}"
pip install -q uv > /dev/null 2>&1
uv pip install -q -e . > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Start Docker
echo ""
echo -e "${YELLOW}🐳 Starting Docker containers...${NC}"
docker-compose up -d > /dev/null 2>&1

# Wait for services
echo -e "${YELLOW}⏳ Waiting for PostgreSQL...${NC}"
until docker exec store_postgres pg_isready -U njshop >/dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ PostgreSQL ready${NC}"

echo -e "${YELLOW}⏳ Waiting for Redis...${NC}"
until docker exec store_redis redis-cli ping >/dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ Redis ready${NC}"

echo -e "${YELLOW}⏳ Waiting for Celery Flower...${NC}"
until curl -s http://localhost:5555 > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ Celery Flower ready${NC}"

# Migrate
echo ""
echo -e "${YELLOW}🗄️  Running migrations...${NC}"
python manage.py migrate --noinput >/dev/null 2>&1
echo -e "${GREEN}✓ Database ready${NC}"

# Create superuser
if ! python manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
    echo -e "${YELLOW}👤 Creating superuser (admin/admin123)...${NC}"
    python manage.py shell <<EOF 2>/dev/null
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@njshop.com', 'admin123')
EOF
    echo -e "${GREEN}✓ Superuser created${NC}"
else
    echo -e "${GREEN}✓ Superuser exists${NC}"
fi

# Final instructions
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ READY TO GO!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📦 Docker Services:${NC}"
docker-compose ps | tail -2
echo ""
echo -e "${BLUE}🚀 Run in NEW terminals:${NC}"
echo ""
echo -e "  ${YELLOW}# Terminal 1: Django Server${NC}"
echo -e "  ${YELLOW}cd backend && source venv/bin/activate${NC}"
echo -e "  ${YELLOW}python manage.py runserver${NC}"
echo ""
echo -e "  ${YELLOW}# Terminal 2: Celery Worker (optional)${NC}"
echo -e "  ${YELLOW}cd backend && source venv/bin/activate${NC}"
echo -e "  ${YELLOW}celery -A ecommerce worker --loglevel=info${NC}"
echo ""
echo -e "  ${YELLOW}# Terminal 3: Frontend${NC}"
echo -e "  ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo -e "${BLUE}🌐 Open in Browser:${NC}"
echo -e "  ${YELLOW}http://localhost:3000${NC}          (Frontend)"
echo -e "  ${YELLOW}http://localhost:8000/admin${NC}    (Admin Panel - admin/admin123)"
echo -e "  ${YELLOW}http://localhost:5555${NC}          (Celery Flower - Task Monitor)"
echo ""
echo -e "${BLUE}📊 Services Status:${NC}"
docker-compose ps
echo ""
echo -e "${BLUE}🛑 Stop Everything:${NC}"
echo -e "  ${YELLOW}docker-compose down${NC}"
echo ""
