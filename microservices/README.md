
# Flight Booking Microservices

This repository contains the microservices architecture for the flight booking application, decomposed from the original monolithic structure.

## Architecture Overview

The application is split into 4 independent microservices:

1. **Backend Service** (Port 8001) - Core flight booking operations
2. **Payment Service** (Port 8002) - Payment processing and transactions
3. **Loyalty Service** (Port 8003) - Loyalty program and points management
4. **UI Service** (Port 8000) - Frontend and API Gateway

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL (if running locally)

### Environment Setup

1. **Clone and navigate to microservices directory:**
```bash
cd microservices
```

2. **Create environment file:**
```bash
cp .env.example .env
```

3. **Update environment variables in `.env`:**
```env
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Database
POSTGRES_DB=flight_booking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### Running with Docker Compose

1. **Build and start all services:**
```bash
docker-compose up --build
```

2. **Run database migrations:**
```bash
# Backend Service
docker-compose exec backend-service python manage.py migrate

# Payment Service
docker-compose exec payment-service python manage.py migrate

# Loyalty Service
docker-compose exec loyalty-service python manage.py migrate
```

3. **Create superuser (optional):**
```bash
docker-compose exec backend-service python manage.py createsuperuser
```

4. **Load initial data:**
```bash
# Load places and flights data
docker-compose exec backend-service python manage.py loaddata initial_data.json

# Setup loyalty tiers
docker-compose exec loyalty-service python manage.py setup_loyalty_data

# Setup bank test data
docker-compose exec payment-service python manage.py setup_bank_data
```

### Service URLs

- **UI Service (Main App)**: http://localhost:8000
- **Backend Service API**: http://localhost:8001/api/
- **Payment Service API**: http://localhost:8002/api/
- **Loyalty Service API**: http://localhost:8003/api/
- **Database**: localhost:5432

## Service Details

### Backend Service (8001)
**Responsibility**: Core flight operations and user management

**Key Endpoints:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/flights/search` - Search flights
- `POST /api/flights/book` - Book flight
- `GET /api/places/search` - Search airports/cities

**Database Tables:**
- Users, Places, Flights, Passengers, Tickets, Week

### Payment Service (8002)
**Responsibility**: Payment processing and financial transactions

**Key Endpoints:**
- `POST /api/payments/create-intent` - Create payment intent
- `POST /api/payments/process` - Process payment
- `POST /api/payments/webhook` - Stripe webhooks
- `GET /api/payments/history/{user_id}` - Payment history

**Database Tables:**
- BankCard, PaymentTransaction

### Loyalty Service (8003)
**Responsibility**: Loyalty program and points management

**Key Endpoints:**
- `GET /api/loyalty/account/{user_id}` - Get loyalty account
- `POST /api/loyalty/earn` - Award points
- `POST /api/loyalty/redeem` - Redeem points
- `GET /api/loyalty/history/{user_id}` - Transaction history

**Database Tables:**
- LoyaltyTier, LoyaltyAccount, PointsTransaction

### UI Service (8000)
**Responsibility**: User