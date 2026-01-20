"""
Test SAGA endpoints across all microservices
"""
import requests
import json

def test_service_health():
    """Test if all services are running"""
    services = {
        'Backend': 'http://localhost:8001/api/health/',
        'Payment': 'http://localhost:8003/health/',
        'Loyalty': 'http://localhost:8002/api/loyalty/',
        'UI': 'http://localhost:8000/'
    }
    
    print("=== Testing Service Health ===")
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")

def test_saga_endpoints():
    """Test individual SAGA endpoints"""
    print("\n=== Testing SAGA Endpoints ===")
    
    # Test data
    test_data = {
        'correlation_id': 'test-123',
        'booking_data': {
            'flight_id': 1,
            'user_id': 1,
            'passengers': [{'first_name': 'Test', 'last_name': 'User', 'gender': 'male'}],
            'contact_info': {'email': 'test@test.com', 'mobile': '1234567890'},
            'flight_fare': 500.0
        }
    }
    
    endpoints = [
        ('Backend Reserve Seat', 'http://localhost:8001/api/saga/reserve-seat/'),
        ('Payment Authorize', 'http://localhost:8003/api/saga/authorize-payment/'),
        ('Loyalty Award Miles', 'http://localhost:8002/api/saga/award-miles/'),
        ('Backend Confirm', 'http://localhost:8001/api/saga/confirm-booking/')
    ]
    
    for name, url in endpoints:
        try:
            response = requests.post(url, json=test_data, timeout=10)
            print(f"✅ {name}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    test_service_health()
    test_saga_endpoints()