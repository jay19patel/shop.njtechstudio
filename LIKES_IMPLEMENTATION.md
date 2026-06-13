# Product Likes Implementation - Complete Guide

## 🎉 What's Been Implemented

### **Backend Features**
✅ **Like Model with Price Snapshot**
- Stores user ID, product ID, price at time of like, and timestamp
- Unique constraint ensures each user can like each product once
- Migration created: `0014_add_price_snapshot_to_like.py`

✅ **Like API Endpoints**
- `POST /api/likes/toggle-like/` - Like/Unlike a product
- `GET /api/likes/is-liked/?product_id=<id>` - Check if product is liked
- `GET /api/likes/my-likes/` - Get user's liked products with price history

✅ **Admin Panel**
- Likes visible in "Customer Management" section
- View all likes with user, product, price snapshot, and date
- Read-only interface (likes created via API only)

### **Frontend Features**
✅ **Product Detail Page**
- Like/unlike button with heart icon
- Visual feedback:
  - **Red (filled)** when liked
  - **Gray (outline)** when not liked
- Login redirect if user not authenticated
- Loading state handling

✅ **User Profile - Liked Products Tab**
- New "Liked Products" section in profile
- Shows grid of liked products with:
  - Product image
  - Product name
  - Current price (live)
  - Price when liked (strikethrough if changed)
  - Date liked
  - "View Product" button
- Empty state message when no likes
- Loading indicator

---

## 🚀 Quick Start Guide

### **Step 1: Start Docker Services (Database, Redis, Celery)**
```bash
cd backend
docker-compose up -d
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Celery Worker** (background tasks)

### **Step 2: Setup Django Environment**
```bash
cd backend

# Option A: Using the startup script (recommended)
./start-dev.sh

# Option B: Manual setup
python -m venv venv
source venv/bin/activate
pip install -e .
python manage.py migrate
python manage.py runserver
```

### **Step 3: Create Admin User (if needed)**
```bash
python manage.py createsuperuser
```

### **Step 4: Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 File Structure

### Backend
```
backend/
├── docker-compose.yml          # Docker services (DB, Redis, Celery)
├── Dockerfile.celery           # Celery worker Docker image
├── start-dev.sh                # Quick setup script
├── SETUP.md                    # Detailed setup guide
├── .env.example                # Environment variables template
├── store/
│   ├── models/like.py          # Like model with price_at_like
│   ├── views/likes.py          # Like API endpoints
│   ├── serializers/like.py     # Like serializers
│   ├── admin.py                # Like admin configuration
│   └── migrations/0014_*.py    # Database migration
└── manage.py                   # Django management
```

### Frontend
```
frontend/
├── lib/api.js                  # API functions (toggleLike, getUserLikes, etc)
├── app/
│   ├── shop/[id]/page.js       # Product detail with like button
│   └── profile/page.js         # Profile with liked products tab
└── components/                 # Components
```

---

## 🔌 Database Schema

### **Like Table**
```sql
store_like (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  product_id INTEGER FOREIGN KEY,
  price_at_like DECIMAL(10, 2),        -- Price snapshot
  created_at DATETIME,
  UNIQUE (user_id, product_id)
)
```

---

## 📡 API Endpoints

### **Toggle Like**
```
POST /api/likes/toggle-like/
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "product_id": 5
}

Response (Liked):
{
  "liked": true,
  "message": "Like added"
}

Response (Unliked):
{
  "liked": false,
  "message": "Like removed"
}
```

### **Check if Liked**
```
GET /api/likes/is-liked/?product_id=5
Authorization: Bearer {token}

Response:
{
  "product_id": 5,
  "is_liked": true,
  "likes_count": 23
}
```

### **Get User's Liked Products**
```
GET /api/likes/my-likes/
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "product_id": 5,
    "product_name": "Handmade Pottery",
    "product_slug": "handmade-pottery",
    "product_image": "https://...",
    "current_price": 450.00,
    "price_when_liked": 500.00,      -- If price changed
    "liked_date": "2026-06-13T10:30:00Z"
  },
  ...
]
```

---

## 🐳 Docker Commands

### **Start Services**
```bash
docker-compose up -d
```

### **Stop Services**
```bash
docker-compose down
```

### **View Logs**
```bash
docker-compose logs -f postgres      # PostgreSQL logs
docker-compose logs -f redis         # Redis logs
docker-compose logs -f celery-worker # Celery logs
```

### **Access Database**
```bash
docker exec -it khusi_postgres psql -U khusi -d khusi
```

### **Access Redis**
```bash
docker exec -it khusi_redis redis-cli
```

---

## ⚙️ Environment Variables

Create `.env` in `backend/` directory:
```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL in Docker)
DATABASE_URL=postgresql://khusi:khusi_password@localhost:5432/khusi
POSTGRES_DB=khusi
POSTGRES_USER=khusi
POSTGRES_PASSWORD=khusi_password

# Redis (in Docker)
REDIS_URL=redis://localhost:6379/1

# Celery (connects to Docker Redis)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Frontend
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Testing the Feature

### **1. Like a Product**
```bash
# From frontend:
1. Go to http://localhost:3000/shop/5 (any product)
2. Click the heart icon
3. See heart turn red and filled
```

### **2. View Liked Products**
```bash
# From frontend:
1. Go to http://localhost:3000/profile
2. Click "Liked Products" tab
3. See all liked products with price history
```

### **3. Check Admin Panel**
```bash
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Go to "Customer Management" → "Likes"
4. See all user likes with details
```

### **4. Test API Directly**
```bash
# Toggle like
curl -X POST http://localhost:8000/api/likes/toggle-like/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 5}'

# Get user likes
curl -X GET http://localhost:8000/api/likes/my-likes/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check if liked
curl -X GET "http://localhost:8000/api/likes/is-liked/?product_id=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 Troubleshooting

### **500 Error When Liking**
**Solution**: Make sure migration is applied
```bash
python manage.py migrate store
python manage.py migrate
```

### **Database Connection Error**
**Solution**: Check if PostgreSQL is running
```bash
docker-compose logs postgres
docker ps | grep postgres
```

### **Redis Connection Error**
**Solution**: Check if Redis is running
```bash
docker exec -it khusi_redis redis-cli ping
# Should output: PONG
```

### **Celery Worker Not Working**
**Solution**: Check Celery logs and restart
```bash
docker-compose logs celery-worker
docker-compose restart celery-worker
```

### **Like Button Not Working on Frontend**
**Solution**: Check browser console for errors
```javascript
// Open browser DevTools (F12)
// Check Console tab for error messages
// Check Network tab to see API calls
```

---

## 📊 Future Enhancements

These features were designed with future expansion in mind:

### **Price Drop Notifications** (Next Phase)
- Monitor price changes for liked products
- Send notifications when price drops
- Use `price_at_like` field for comparison

### **Wishlist Features**
- Add quantities to liked products
- Share wishlists with others
- Birthday wishlists

### **Analytics**
- Most liked products
- Trending products
- User preference analysis

---

## 📝 Notes

- **Authentication Required**: Likes require user login
- **Unique Constraint**: Each user can only like each product once
- **Price Snapshot**: Stores price at time of like (useful for price tracking)
- **Real-time Updates**: Prices in profile update automatically
- **Admin Control**: Likes can only be created/deleted via API, not admin panel

---

## 🎯 What You Need to Do Next

1. **Start Docker**:
   ```bash
   cd backend && docker-compose up -d
   ```

2. **Setup Django**:
   ```bash
   cd backend && ./start-dev.sh
   ```

3. **Start Frontend**:
   ```bash
   cd frontend && npm run dev
   ```

4. **Test the Feature**:
   - Visit http://localhost:3000/shop/1
   - Click the like button
   - Check your profile's "Liked Products" tab

---

## ✅ Checklist

- [x] Like/Unlike functionality
- [x] Price snapshot storage
- [x] Admin panel integration
- [x] Frontend like button
- [x] Profile liked products display
- [x] API endpoints
- [x] Database migration
- [x] Docker setup for dev
- [x] Error handling
- [x] Authentication checks
- [x] Loading states
- [x] Documentation

---

**Happy coding! 🚀**

For more details, see:
- Backend: `backend/SETUP.md`
- API Documentation: `backend/apis.md` (update if needed)
