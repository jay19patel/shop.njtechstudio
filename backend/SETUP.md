# NJShop Backend Setup Guide

## Prerequisites
- Python 3.13+
- Docker & Docker Compose
- PostgreSQL (via Docker)
- Redis (via Docker)

## Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Machine (Host)                         │
│                                                                  │
│  ┌───────────────────────────────┐  ┌──────────────────────┐   │
│  │  Django Dev Server (port 8000)│  │  Node.js Frontend    │   │
│  │  python manage.py runserver   │  │  (port 3000)         │   │
│  └───────────┬───────────────────┘  └──────────────────────┘   │
│              │                                                   │
│              ├──► Database (PostgreSQL)                         │
│              ├──► Redis                                         │
│              └──► Celery Worker                                 │
└──────────────┼──────────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
    ┌──▼───┐        ┌──▼────┐
    │Docker│        │Docker │
    │ DB   │        │Redis  │
    └──────┘        └───────┘
```

## Quick Start

### 1. Start Docker Services (Database, Redis, Celery)
```bash
cd backend
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Celery Worker

### 2. Setup Django Environment
```bash
cd backend
python -m venv venv          # Create virtual environment
source venv/bin/activate     # Activate (macOS/Linux)
# For Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
# or with uv:
uv pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create `.env` file in `backend/` directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://khusi:khusi_password@localhost:5432/khusi
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
FRONTEND_URL=http://localhost:3000
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (for Admin Panel)
```bash
python manage.py createsuperuser
```

### 6. Start Django Development Server
```bash
python manage.py runserver
# Server runs at http://localhost:8000
# Admin panel at http://localhost:8000/admin
```

### 7. Start Frontend (in separate terminal)
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:3000
```

## Commands Reference

### Django Management
```bash
# Migrations
python manage.py makemigrations      # Create new migrations
python manage.py migrate             # Apply migrations
python manage.py showmigrations      # Show migration status

# Admin
python manage.py createsuperuser     # Create admin user
python manage.py changepassword      # Change user password

# Development
python manage.py runserver           # Start dev server
python manage.py shell               # Django shell
python manage.py dbshell             # Database shell
```

### Docker Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres      # PostgreSQL logs
docker-compose logs -f redis         # Redis logs
docker-compose logs -f celery-worker # Celery logs

# Enter PostgreSQL
docker exec -it khusi_postgres psql -U khusi -d khusi

# Enter Redis
docker exec -it khusi_redis redis-cli
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5432 (PostgreSQL)
lsof -i :5432

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Error
```bash
# Check if PostgreSQL container is running
docker ps | grep khusi_postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Reset PostgreSQL
docker-compose down
docker volume rm njtechstudio_khusi_postgres
docker-compose up -d postgres
```

### Celery Not Working
```bash
# Check Celery worker status
docker-compose logs celery-worker

# Restart Celery worker
docker-compose restart celery-worker
```

### Redis Connection Issues
```bash
# Test Redis connection
docker exec -it khusi_redis redis-cli ping
# Should return: PONG
```

## File Structure
```
backend/
├── docker-compose.yml      # Docker services (DB, Redis, Celery)
├── Dockerfile.celery       # Celery worker image
├── manage.py               # Django management script
├── ecommerce/              # Django settings
├── store/                  # Main app
│   ├── models/             # Database models
│   ├── views/              # API endpoints
│   ├── serializers/        # DRF serializers
│   ├── admin.py            # Admin panel configuration
│   └── ...
├── .env.example            # Example environment variables
└── pyproject.toml          # Project dependencies
```

## API Endpoints

### Likes
- `POST /api/likes/toggle-like/` - Toggle like for product
- `GET /api/likes/is-liked/?product_id=<id>` - Check if liked
- `GET /api/likes/my-likes/` - Get user's liked products

### Products
- `GET /api/products/` - List products
- `GET /api/products/<id>/` - Product details

### Orders
- `GET /api/orders/` - User's orders
- `POST /api/orders/` - Create order

## Notes
- Django runs on your machine, connects to Docker database
- Celery worker runs in Docker container
- All data is persisted in Docker volumes
- Frontend communicates with Django via API
