# Local Development Setup (Without Docker)

Since Docker is not available on this system, here's how to run the microservices locally:

## Prerequisites

1. **Python 3.9+** ✅ (Already installed)
2. **PostgreSQL** (Need to install)
3. **pip** ✅ (Already available)

## Setup Instructions

### 1. Install PostgreSQL
Download and install PostgreSQL from: https://www.postgresql.org/download/windows/

Create databases:
```sql
CREATE DATABASE flight_booking;
CREATE USER flight_user WITH PASSWORD 'flight_password';
GRANT ALL PRIVILEGES ON DATABASE flight_booking TO flight_user;
```

### 2. Set Environment Variables
Create a `.env` file in the microservices directory:
```env
# Database
DB_NAME=flight_booking
DB_USER=flight_user
DB_PASSWORD=flight_password
DB_HOST=localhost
DB_PORT=5432

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Service URLs
BACKEND_SERVICE_URL=http://localhost:8001
PAYMENT_SERVICE_URL=http://localhost:8002
LOYALTY_SERVICE_URL=http://localhost:8003
UI_SERVICE_URL=http://localhost:8000
```

### 3. Start Backend Service (Port 8001)

```bash
cd microservices/backend-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

### 4. Start Payment Service (Port 8002)
```bash
cd microservices/payment-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

### 5. Start Loyalty Service (Port 8003)
```bash
cd microservices/loyalty-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8003
```

### 6. Start UI Service (Port 8000)
```bash
cd microservices/ui-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

## Service URLs

- **UI Service (Main App)**: http://localhost:8000
- **Backend Service API**: http://localhost:8001/api/
- **Payment Service API**: http://localhost:8002/api/
- **Loyalty Service API**: http://localhost:8003/api/

## Current Status

✅ **Backend Service**: Fully implemented and ready
⚠️  **Payment Service**: Partially created (needs completion)
⚠️  **Loyalty Service**: Not created yet
⚠️  **UI Service**: Not created yet

## Next Steps

1. Install PostgreSQL
2. Complete the missing services
3. Start services individually in separate terminals
4. Test the APIs

## Alternative: Use SQLite for Development

If PostgreSQL installation is not possible, you can modify the Django settings to use SQLite:

```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

This will allow you to run the services without PostgreSQL installation.