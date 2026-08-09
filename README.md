# LandMarket - India Real Estate Marketplace

A comprehensive real estate marketplace platform focused on the Indian market, featuring property listings, geolocation services, real-time chat, and mobile-first design.

## 🏗️ Architecture

- **Backend**: Django 5.0 + Django REST Framework + PostGIS
- **Frontend**: React 19 + Vite + TailwindCSS + PWA
- **Database**: PostgreSQL 16 + PostGIS for geospatial data
- **Cache/Queue**: Redis 7.x for caching, sessions, and background jobs
- **Search**: Elasticsearch 8.x for advanced property search
- **Real-time**: Django Channels + WebSocket for chat and notifications
- **Mobile**: Progressive Web App + Capacitor for app store deployment

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (optional, for local frontend development)
- Python 3.11+ (optional, for local backend development)

### Development Setup (5 minutes)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd landmarket

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Done! Services are running
```

### Access Points

- **Frontend**: http://localhost:3000 (React PWA)
- **Backend API**: http://localhost:8000/api/ (REST endpoints)
- **Admin Panel**: http://localhost:8000/admin/ (Django admin)
- **API Docs**: http://localhost:8000/api/docs/ (Interactive Swagger)
- **API ReDoc**: http://localhost:8000/api/redoc/ (Alternative docs)

### First Steps

1. **Login to Admin**: http://localhost:8000/admin/
2. **Explore API**: http://localhost:8000/api/docs/
3. **View Frontend**: http://localhost:3000
4. **Read**: [Getting Started Guide](GETTING_STARTED.md)

## 📱 Features

### Phase 1 - MVP (✅ COMPLETE - Ready for Development)
- ✅ Multi-role authentication (Buyer, Vendor, Broker, Admin)
- ✅ Property listings with Indian land-specific fields (Patta, Chitta, Survey#)
- ✅ Advanced search with geolocation and filtering
- ✅ Real-time chat infrastructure (WebSocket ready)
- ✅ Site visit scheduling and management
- ✅ Mobile-first PWA design
- ✅ Admin approval workflow
- ✅ Wishlist/save properties functionality
- ✅ Property reviews and ratings
- ✅ Complete REST API with Swagger/ReDoc documentation
- ✅ PostgreSQL + PostGIS for geospatial queries
- ✅ Docker environment for local development

### Phase 2 - Trust & Scale (Planned)
- 🔄 Property verification system with document OCR
- 🔄 Subscription plans and payment integration (Razorpay)
- 🔄 Advanced CRM for vendors and brokers
- 🔄 Mobile app store deployment (Capacitor)
- 🔄 Enhanced map features and property comparison
- 🔄 Elasticsearch integration for powerful search

### Phase 3 - Intelligence (Future)
- 📋 AI-powered property recommendations
- 📋 Market analytics and insights
- 📋 Investment potential scoring
- 📋 Load testing and horizontal scaling

## 🏢 User Roles

| Role | Capabilities |
|------|-------------|
| **Buyer** | Search properties, save favorites, chat with vendors, schedule visits |
| **Vendor** | List properties, manage leads, chat with buyers, view analytics |
| **Broker** | Manage properties for multiple owners, advanced CRM tools |
| **Admin** | Approve properties, manage users, platform analytics |

## 🗺️ Indian Market Focus

- **Location Data**: State/District/City hierarchies for India
- **Land Records**: Patta, Chitta, Encumbrance Certificate support
- **Area Units**: Automatic conversion between Sqft/Cent/Ground/Acre/Hectare  
- **Legal Compliance**: RERA registration tracking
- **Payment**: Razorpay integration for Indian payment methods

## 🔧 Development

### Project Structure
```
landmarket/
├── backend/           # Django REST API
├── frontend/          # React PWA
├── infrastructure/    # Docker, deployment configs
├── docs/             # API documentation, architecture
└── scripts/          # Setup and deployment scripts
```

### API Documentation
- Interactive API docs available at `/api/docs/`
- OpenAPI 3.0 specification
- Postman collection in `/docs/api/`

### Database
- PostgreSQL with PostGIS extension for geospatial queries
- Comprehensive indexing strategy for performance
- Automated migrations and seed data

## 🚢 Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

See `docs/deployment.md` for detailed production setup.

## 🧪 Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests  
cd frontend && npm test

# Integration tests
npm run test:e2e
```

## 📊 Performance

- **Search**: Elasticsearch with geospatial indexing
- **Caching**: Redis cache-aside pattern for hot data
- **Images**: WebP compression + CDN delivery
- **Database**: Optimized queries with PostGIS indexes
- **Mobile**: <3s load time on 3G networks

## 🔐 Security

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Input validation and sanitization
- Rate limiting on public endpoints
- HTTPS enforcement
- Secure file uploads with virus scanning

## 📄 License

Copyright (c) 2026 LandMarket. All rights reserved.

---

For detailed setup instructions, see the [Development Guide](docs/development.md).