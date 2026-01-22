
# AA Flight Booking System - Database Setup and Microservices Guide

## Overview
This document provides complete instructions for setting up the database and starting all microservices for the AA Flight Booking System. Follow these steps to get the system running smoothly.

## Prerequisites
- Python 3.12 installed
- Django and required packages (see requirements.txt in each service)
- CSV data file: `flights_export_20260121_195421.csv`

## Database Setup

### 1. Database Import Script Location
The database import script is located at:
```
AA_Flight_booking/microservices/backend-service/import_flights_db.py
```

### 2. CSV Data File
The CSV file with flight data is already placed at:
```
AA_Flight_booking/microservices/backend-service/flights_export_20260121_195421.csv
```

### 3. Database Creation Steps

#### Step 1: Navigate to Backend Service
```bash
cd AA_Flight_booking/microservices/backend-service
```

#### Step 2: Run Database Migrations
```bash
python3.12 manage.py migrate
```

#### Step 3: Execute Database Import Script
```bash
python3.12 import_flights_db.py
```

**Expected Output:**
```
SUCCESS: Django setup successful - models imported
FLIGHT DATABASE RECREATION TOOL
==================================================
Clearing existing data...
SUCCESS: Existing data cleared
Setting up week data...
SUCCESS: Week data setup complete
Importing flights from CSV...
   Imported 1000 flights...
   Imported 2000 flights...
   ...
   Imported 12000 flights...
SUCCESS: Import completed!
   Successfully imported: 12658 flights
   Skipped: 0 flights
Verifying database...
   Flights: 12658
   Places: 60
   Weeks: 7
SUCCESS: Database recreation successful!
   Frontend/Backend should now work with full flight data
```

#### Step 4: Verify Database
```bash
python3.12 manage.py shell -c "from flight.models import Flight, Place, Week; print('Flights:', Flight.objects.count()); print('Places:', Place.objects.count()); print('Weeks:', Week.objects.count())"
```

## Microservices Architecture

The system consists of 4 microservices:

1. **UI Service** (Port 8000) - Frontend interface
2. **Backend Service** (Port 8001) - Flight data and booking logic
3. **Loyalty Service** (Port 8002) - Loyalty points management
4. **Payment Service** (Port 8003) - Payment processing

## Starting Microservices

### Method 1: Individual Service Startup

#### 1. Start Backend Service (Port 8001)
```bash
cd AA_Flight_booking/microservices/backend-service
python3.12 manage.py runserver 8001
```

#### 2. Start Loyalty Service (Port 8002)
```bash
cd AA_Flight_booking/microservices/loyalty-service
python3.12 manage.py runserver 8002
```

#### 3. Start Payment Service (Port 8003)
```bash
cd AA_Flight_booking/microservices/payment-service
python3.12 manage.py runserver 8003
```

#### 4. Start UI Service (Port 8000)
```bash
cd AA_Flight_booking/microservices/ui-service
python3.12 manage.py runserver 8000
```

### Method 2: Automated Startup (Windows)

#### Start All Services with Individual Windows
```bash
# Backend Service
cd "AA_Flight_booking\microservices\backend-service" && start "Backend Service" python3.12 manage.py runserver 8001

# Loyalty Service
cd "AA_Flight_booking\microservices\loyalty-service" && start "Loyalty Service" python3.12 manage.py runserver 8002

# Payment Service
cd "AA_Flight_booking\microservices\payment-service" && start "Payment Service" python3.12 manage.py runserver 8003

# UI Service
cd "AA_Flight_booking\microservices\ui-service" && start "UI Service" python3.12 manage.py runserver 8000
```

## Service Health Check

### Verify All Services Are Running

#### 1. Backend Service Health Check
```bash
curl http://localhost:8001/api/health/
```
Expected Response: `{"status": "healthy", "service": "backend-service"}`

#### 2. UI Service Check
Open browser: `http://localhost:8000`

#### 3. Test Database Integration
```bash
curl "http://localhost:8001/api/places/search/?q=Delhi"
```
Expected Response: Flight places data from Delhi

## API Endpoints

### Backend Service (Port 8001)
- Health Check: `GET /api/health/`
- Places Search: `GET /api/places/search/?q={query}`
- Flight Search: `GET /api/flights/search/?origin={code}&destination={code}&date={date}`
- Flight Detail: `GET /api/flights/{flight_id}/`
- Book Flight: `POST /api/flights/book/`
- SAGA Endpoints: `/api/saga/*`

### UI Service (Port 8000)
- Main Interface: `http://localhost:8000`
- Flight Search and Booking Interface

### Loyalty Service (Port 8002)
- Loyalty points management
- SAGA compensation endpoints

### Payment Service (Port 8003)
- Payment processing
- SAGA payment authorization

## Database Information

### Database Statistics
- **Flights**: 12,658 records
- **Places**: 60 airports/cities
- **Weeks**: 7 days of the week
- **Database Type**: SQLite3
- **Location**: `AA_Flight_booking/microservices/backend-service/db.sqlite3`

### Sample Data
- **Airlines**: Various Indian and international airlines
- **Routes**: Domestic and international flights
- **Cities**: Major Indian cities (Delhi, Mumbai, Bangalore, Chennai, etc.)
- **Fare Classes**: Economy, Business, First Class

## Troubleshooting

### Common Issues

#### 1. Python Version Error
**Error**: `ModuleNotFoundError: No module named 'cgi'`
**Solution**: Use Python 3.12 instead of Python 3.13
```bash
python3.12 manage.py runserver
```

#### 2. Database Not Found
**Error**: Database file missing
**Solution**: Run the database import script:
```bash
cd AA_Flight_booking/microservices/backend-service
python3.12 import_flights_db.py
```

#### 3. Port Already in Use
**Error**: Port 8000/8001/8002/8003 already in use
**Solution**: Kill existing processes or use different ports:
```bash
# Kill process on specific port (Windows)
netstat -ano | findstr :8001
taskkill /PID {process_id} /F
```

#### 4. CSV File Not Found
**Error**: `ERROR: CSV file not found: flights_export_20260121_195421.csv`
**Solution**: Ensure CSV file is in the backend-service directory:
```
AA_Flight_booking/microservices/backend-service/flights_export_20260121_195421.csv
```

## Development Workflow

### 1. Initial Setup (One-time)
1. Set up database using import script
2. Verify all services start successfully
3. Test API endpoints

### 2. Daily Development
1. Start all microservices
2. Access UI at `http://localhost:8000`
3. Use backend APIs for testing

### 3. Testing
- Unit tests available in each service
- Integration tests in `/temp_cleanup/test_files/`
- SAGA pattern testing available

## Quick Start Summary

1. **Setup Database**: `cd AA_Flight_booking/microservices/backend-service && python3.12 import_flights_db.py`
2. **Start Services**: Run all 4 microservices on ports 8000-8003
3. **Access Application**: Open `http://localhost:8000`
4. **Verify Health**: Check `http://localhost:8001/api/health/`

## Support

For issues or questions:
- Check troubleshooting section above
- Review service logs in terminal windows
- Verify all services are running on correct ports

---

**Document Created**: January 22, 2026
**Last Updated**: January 22, 2026
**Database Records**: 12,658 flights successfully imported
**System Status**: Fully operational with all microservices