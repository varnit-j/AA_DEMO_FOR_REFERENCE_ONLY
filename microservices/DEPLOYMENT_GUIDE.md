
# Flight Booking Microservices Deployment Guide

## Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Install Docker Desktop (Windows/Mac) or Docker Engine (Linux)
   # Verify installation
   docker --version
   docker-compose --version
   ```

2. **Environment Variables**
   Create `.env` file in the microservices directory:
   ```bash
   # Stripe Configuration
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
   STRIPE_SECRET_KEY=sk_test_your_secret_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

## Quick Start

### 1. Clone and Navigate
```bash
cd microservices/
```

### 2. Build and Start All Services
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Initialize Database
```bash
# Run migrations on backend service
docker-compose exec backend-service python manage.py migrate

# Create superuser (optional)
docker-compose exec backend-service python manage.py createsuperuser

# Load initial data
docker-compose exec backend-service python manage.py loaddata initial_data.json
```

## Service URLs

- **UI Service (Frontend)**: http://localhost:8000
- **Backend Service (API)**: http://localhost:8001
- **Payment Service**: http://localhost:8002
- **Loyalty Service**: http://localhost:8003
- **PostgreSQL Database**: localhost:5432

## API Documentation

### Backend Service (Port 8001)

#### Authentication
```bash
# Register user
POST /api/auth/register/
{
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "password": "testpass123",
  "password_confirm": "testpass123"
}

# Login
POST /api/auth/login/
{
  "username": "testuser",
  "password": "testpass123"
}

# Logout
POST /api/auth/logout/
Headers: Authorization: Token <your_token>
```

#### Flight Search
```bash
# Search places
GET /api/places/search/?q=delhi

# Search flights
GET /api/flights/search/?origin=DEL&destination=BOM&depart_date=2024-01-15&seat_class=economy
```

#### Bookings
```bash
# Create booking
POST /api/bookings/create/
Headers: Authorization: Token <your_token>
{
  "flight_id": 1,
  "flight_date": "2024-01-15",
  "seat_class": "economy",
  "passengers": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "gender": "male"
    }
  ],
  "mobile": "9876543210",
  "email": "john@example.com",
  "country_code": "+91"
}

# List user bookings
GET /api/bookings/
Headers: Authorization: Token <your_token>
```

## Development Workflow

### Individual Service Development
```bash
# Start only specific services
docker-compose up postgres backend-service

# Rebuild specific service
docker-compose build backend-service
docker-compose up -d backend-service

# View service logs
docker-compose logs -f backend-service
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d flight_booking

# Backup database
docker-compose exec postgres pg_dump -U postgres flight_booking > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres flight_booking < backup.sql
```

### Debugging
```bash
# Execute commands in service container
docker-compose exec backend-