
# Flight Booking Microservices Architecture

## Overview
This document outlines the decomposition of the monolithic flight booking application into 4 independent microservices for better scalability, maintainability, and fault tolerance.

## Microservices Architecture

### 1. Backend Service (Core Flight Booking)
**Port**: 8001
**Responsibility**: Core flight operations and user management
**Database**: PostgreSQL (flights_db)

#### Components:
- User authentication and management
- Flight search and booking
- Airport and place management
- Ticket generation and management
- Order coordination

#### Files/Modules:
```
backend-service/
├── flight/
│   ├── models.py (User, Place, Flight, Passenger, Ticket)
│   ├── views.py (search, booking, user management)
│   ├── utils.py
│   └── admin.py
├── capstone/
│   ├── settings.py
│   ├── urls.py
│   └── utils.py
├── Data/ (airports, flights CSV)
├── manage.py
└── requirements.txt
```

#### API Endpoints:
- `GET /api/flights/search` - Search flights
- `POST /api/flights/book` - Book flight
- `GET /api/tickets/{id}` - Get ticket details
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User authentication
- `GET /api/places/search` - Search airports/cities

### 2. Payment Service
**Port**: 8002
**Responsibility**: Payment processing and financial transactions
**Database**: PostgreSQL (payments_db)

#### Components:
- Stripe payment integration
- Mock banking system
- Payment validation and processing
- Transaction history
- Refund management

#### Files/Modules:
```
payment-service/
├── apps/
│   ├── payments/
│   │   └── stripe_client.py
│   └── banking/
│       ├── models.py (BankCard, PaymentTransaction)
│       └── service.py (MockBankingService)
├── payments/
│   ├── views.py
│   ├── webhooks.py
│   └── urls.py
├── settings.py
└── requirements.txt
```

#### API Endpoints:
- `POST /api/payments/create-intent` - Create payment intent
- `POST /api/payments/process` - Process payment
- `POST /api/payments/webhook` - Stripe webhooks
- `GET /api/payments/history/{user_id}` - Payment history
- `POST /api/payments/refund` - Process refund

### 3. Loyalty Service
**Port**: 8003
**Responsibility**: Loyalty program and points management
**Database**: PostgreSQL (loyalty_db)

#### Components:
- Points earning and redemption
- Tier management
- Transaction history
- Points expiry handling
- Loyalty dashboard

#### Files/Modules:
```
loyalty-service/
├── apps/
│   └── loyalty/
│       ├── models.py (LoyaltyTier, LoyaltyAccount, PointsTransaction)
│       ├── service.py (LoyaltyService)
│       ├── views.py
│       ├── admin.py
│       └── management/commands/
├── settings.py
└── requirements.txt
```

#### API Endpoints:
- `GET /api/loyalty/account/{user_id}` - Get loyalty account
- `POST /api/loyalty/earn` - Award points
- `POST /api/loyalty/redeem` - Redeem points
- `GET /api/loyalty/history/{user_id}` - Transaction history
- `GET /api/loyalty/tiers` - Get tier information

### 4. UI Service (Frontend + API Gateway)
**Port**: 8000
**Responsibility**: User interface and API orchestration
**Database**: None (stateless)

#### Components:
- Frontend templates and static files
- API Gateway for routing requests