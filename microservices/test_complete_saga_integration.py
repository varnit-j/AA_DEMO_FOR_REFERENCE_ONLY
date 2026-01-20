
"""
Complete SAGA Integration Test
Tests all services and endpoints to ensure everything is working
"""
import requests
import json
import time

# Service endpoints
BACKEND_SERVICE = "http://localhost:8001"
LOYALTY_SERVICE = "http://localhost:8002"
PAYMENT_SERVICE = "http://localhost:8003"
UI_SERVICE = "http://localhost:8000"

def test_service_health():
    """Test if all services are running"""
    print("🏥 Testing Service Health")
    print("=" * 50)
    
    services = [
        ("Backend Service", f"{BACKEND_SERVICE}/api/health/"),
        ("Loyalty Service", f"{LOYALTY_SERVICE}/api/loyalty/"),
        ("Payment Service", f"{PAYMENT_SERVICE}/health/"),
        ("UI Service", f"{UI_SERVICE}/")
    ]
    
    all_healthy = True
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} - HEALTHY")
            else:
                print(f"❌ {name} - UNHEALTHY (Status: {response.status_code})")
                all_healthy = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} - CONNECTION FAILED")
            all_healthy = False
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")
            all_healthy = False
    
    return all_healthy

def test_basic_endpoints():
    """Test basic flight booking endpoints"""
    print("\n🛫 Testing Basic Flight Endpoints")
    print("=" * 50)
    
    # Test flight search
    print("\n1. Testing Flight Search...")
    try:
        response = requests.get(f"{BACKEND_SERVICE}/api/flights/search/", params={
            'origin': 'DFW',
            'destination': 'ORD',
            'depart_date': '2026-01-20',
            'seat_class': 'economy'
        })
        
        if response.status_code == 200:
            data = response.json()
            flights = data.get('flights', [])
            print(f"   ✅ Found {len(flights)} flights")
            return flights[0] if flights else None
        else:
            print(f"   ❌ Flight search failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Flight search error: {e}")
        return None

def test_saga_endpoints():
    """Test individual SAGA endpoints"""
    print("\n🔄 Testing SAGA Endpoints")
    print("=" * 50)
    
    correlation_id = "test-integration-123"
    booking_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [{"first_name": "John", "last_name": "Doe", "gender": "male"}],
        "contact_info": {"email": "john@test.com", "mobile": "1234567890"},
        "flight_fare": 500.0
    }
    
    # Test ReserveSeat
    print("\n1. Testing ReserveSeat...")
    try:
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/reserve-seat/", json={
            "correlation_id": correlation_id,
            "booking_data": booking_data,
            "simulate_failure": False
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ ReserveSeat - SUCCESS")
            else:
                print(f"   ❌