# LandMarket - Getting Started Guide

## 🎯 Project Status

**Phase 1 MVP Foundation**: ✅ Complete and Ready for Development

The complete backend architecture, database schema, API endpoints, and frontend structure have been scaffolded. You now have a solid foundation to build the actual features.

---

## 🚀 Quick Start (First Time)

### 1. **Prerequisites**
- Docker Desktop installed and running
- Node.js 18+ (for frontend development)
- Git for version control
- Text editor (VS Code recommended)

### 2. **Initial Setup**

```bash
# Clone the project
cd landmarket

# Create environment file
cp .env.example .env

# Optional: Update .env with your actual API keys
# - GOOGLE_MAPS_API_KEY
# - RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET
```

### 3. **Start Development Environment**

```bash
# Start all services (database, cache, search, backend, frontend)
docker-compose up -d

# Check if all services are running
docker-compose ps

# You should see 7 services: db, redis, elasticsearch, backend, celery, celery-beat, frontend
```

### 4. **Initialize Database**

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create admin user
docker-compose exec backend python manage.py createsuperuser

# (Follow prompts: email, password, role=admin)

# Load initial data (optional)
docker-compose exec backend python manage.py loaddata initial_data.json
```

### 5. **Access Applications**

Open in your browser:

| Application | URL | Purpose |
|-------------|-----|---------|
| Frontend App | http://localhost:3000 | React PWA application |
| Backend API | http://localhost:8000/api/ | REST API endpoints |
| API Docs | http://localhost:8000/api/docs/ | Interactive API documentation |
| Admin Panel | http://localhost:8000/admin/ | Django administration |

---

## 📁 Understanding the Project Structure

### Backend (`backend/`)
```
apps/
├── authentication/    - User login, registration, profiles
├── properties/       - Property listings, search, reviews
├── messaging/        - Chat, notifications, enquiries
├── search/          - Search engine integration (TODO)
├── admin_panel/     - Admin features (TODO)
└── core/            - Shared utilities, permissions
```

### Frontend (`frontend/`)
```
src/
├── components/      - Reusable React components
├── pages/          - Route pages
├── stores/         - Zustand state management
├── services/       - API integration
├── hooks/          - Custom React hooks
└── utils/          - Helper utilities
```

---

## 🔨 Development Workflow

### Backend Development

#### Running Tests
```bash
# Run backend tests
docker-compose exec backend python manage.py test

# Run specific app tests
docker-compose exec backend python manage.py test apps.properties
```

#### Django Shell
```bash
# Access Django shell
docker-compose exec backend python manage.py shell

# Example queries:
# from apps.properties.models import Property
# Property.objects.count()
```

#### Creating Migrations
```bash
# After modifying models
docker-compose exec backend python manage.py makemigrations

# Apply migrations
docker-compose exec backend python manage.py migrate
```

#### Admin Interface
1. Go to http://localhost:8000/admin/
2. Login with your superuser credentials
3. Browse and manage models

### Frontend Development

#### Running Tests
```bash
# Inside frontend container or locally
cd frontend
npm test

# Run with coverage
npm test -- --coverage
```

#### Hot Reload
- Changes to React files automatically reload at http://localhost:3000
- API documentation automatically updates

#### Building for Production
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

---

## 📚 Key API Endpoints

### Authentication
```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+919876543210",
    "role": "buyer",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Properties
```bash
# List properties (requires authentication)
curl -X GET http://localhost:8000/api/properties/ \
  -H "Authorization: Bearer <your-access-token>"

# Create property (vendors only)
curl -X POST http://localhost:8000/api/properties/ \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "2 Acres Agricultural Land",
    "description": "Well developed land...",
    "property_type": "agricultural",
    "purpose": "sale",
    "price": 500000,
    "total_area": 2,
    "area_unit": "acre",
    "survey_number": "123/456",
    "address": "...",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
    "pincode": "641009"
  }'

# Get nearby properties
curl -X GET 'http://localhost:8000/api/properties/nearby/?latitude=13.0827&longitude=80.2707&radius_km=10' \
  -H "Authorization: Bearer <your-access-token>"
```

Full API documentation available at http://localhost:8000/api/docs/

---

## 🔄 Common Development Tasks

### Adding a New API Endpoint

1. **Create the view in `apps/your_app/views.py`**
```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class YourViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        # Your logic here
        return Response({'message': 'Success'})
```

2. **Create serializer in `apps/your_app/serializers.py`**
```python
from rest_framework import serializers

class YourSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = ['field1', 'field2']
```

3. **Register in `apps/your_app/urls.py`**
```python
router.register(r'your-endpoint', YourViewSet, basename='your-endpoint')
```

4. **Add to main URLs in `config/urls.py`**
```python
path('api/', include('apps.your_app.urls')),
```

### Adding a Frontend Component

1. **Create component in `frontend/src/components/`**
2. **Import and use in pages**
3. **Test with `npm test`**
4. **Check browser at http://localhost:3000`**

---

## 🐛 Debugging

### Backend Logs
```bash
# View logs in real-time
docker-compose logs -f backend

# View specific service
docker-compose logs -f frontend
```

### Database Inspection
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U landmarket_user -d landmarket

# List tables
\dt

# Query properties
SELECT * FROM properties LIMIT 5;
```

### API Testing
- Use http://localhost:8000/api/docs/ for interactive testing
- Or use Postman/Insomnia for API requests
- Check browser DevTools Network tab for frontend requests

---

## 🔧 Troubleshooting

### Services won't start
```bash
# Check service logs
docker-compose logs

# Restart services
docker-compose restart

# Full reset (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### Database migration errors
```bash
# Check migration status
docker-compose exec backend python manage.py showmigrations

# Rollback if needed
docker-compose exec backend python manage.py migrate apps.app_name zero
```

### Frontend not updating
```bash
# Clear cache and restart
docker-compose restart frontend

# Or manually in browser: Ctrl+Shift+R (hard refresh)
```

---

## 📊 Database Models

All models are documented in their respective `apps/*/models.py` files:

- **Users**: Custom user model with roles
- **Properties**: Complete property listing with Indian-specific fields
- **Messaging**: Chat, notifications, enquiries
- **And more...**

Visit http://localhost:8000/admin/ to see all models and their relationships.

---

## 🚀 Ready to Build?

### Phase 1 TODO (Currently Scaffolded):

**Sprint 1 - Foundation** ✅
- [x] Authentication system
- [x] Property models & APIs
- [x] Database schema

**Sprint 2 - Core Features** (IN PROGRESS)
- [ ] Search implementation
- [ ] Real-time chat (WebSocket)
- [ ] Frontend property pages
- [ ] Frontend search/map views

**Sprint 3 - Communication** (PLANNED)
- [ ] Enquiry management
- [ ] Site visit scheduling
- [ ] Notifications

**Sprint 4 - Polish** (PLANNED)
- [ ] PWA optimization
- [ ] Performance tuning
- [ ] Mobile responsiveness

### Start Working On:

1. **Search Implementation**
   - Implement Elasticsearch integration in `apps/search/`
   - Add search endpoints
   - Test geo-spatial queries

2. **Frontend Features**
   - Build property listing page
   - Implement search UI
   - Create map view

3. **Testing**
   - Write tests for APIs
   - Add integration tests
   - Test geolocation features

---

## 📖 Learning Resources

### Project Documentation
- API Docs: http://localhost:8000/api/docs/
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- React Docs: https://react.dev/

### Indian Land Records
- Understanding Patta, Chitta, EC: See `docs/india_land_records.md`
- Area conversions: 1 Acre = 43,560 sqft = 100 cents = 10 grounds

---

## ✅ Checklist for Next Steps

- [ ] Services running (`docker-compose ps` shows all healthy)
- [ ] Database initialized (`python manage.py showmigrations` shows applied)
- [ ] Admin panel accessible (http://localhost:8000/admin/)
- [ ] API docs working (http://localhost:8000/api/docs/)
- [ ] Frontend loads (http://localhost:3000/)
- [ ] Can create superuser
- [ ] Can view API schema

---

## 🎓 Need Help?

1. **API Questions**: Check http://localhost:8000/api/docs/
2. **Code Structure**: Read docstrings in model/view files
3. **Database**: Use Django admin interface
4. **Frontend**: Check React component files
5. **Errors**: Check `docker-compose logs`

---

## 🎉 You're Ready!

The foundation is complete. Start building features by:

1. Choosing a feature from the TODO list
2. Implementing it (backend API first)
3. Testing in http://localhost:8000/api/docs/
4. Building frontend components
5. Testing end-to-end

Good luck! 🚀

---

**Last Updated**: August 4, 2026  
**Phase**: 1 - MVP Foundation  
**Status**: Ready for Feature Development