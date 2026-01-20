"""
Simple test for SAGA endpoints
"""
import requests
import json

def test_services():
    """Test if all services are running"""
    services = {
        'Backend': 'http://localhost:8001/api/health/',
        'Payment': 'http://localhost:8003/health/',
        'Loyalty': 'http://localhost:8002/api/loyalty/',
    }
    
    print("=== Testing Service Health ===")
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            print(f"OK {name}: {response.status_code}")
        except Exception as e:
            print(f"ERROR {name}: {e}")

def test_payment_saga():
    """Test payment SAGA endpoint"""
    print("\n=== Testing Payment SAGA ===")
    try:
        url = 'http://localhost:8003/api/saga/authorize-payment/'
        data = {
            'correlation_id': 'test-123',
            'booking_data': {'flight_fare': 500.0}
        }
        response = requests.post(url, json=data, timeout=10)
        print(f"Payment SAGA: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Payment SAGA Error: {e}")

def test_loyalty_saga():
    """Test loyalty SAGA endpoint"""
    print("\n=== Testing Loyalty SAGA ===")
    try:
        url = 'http://localhost:8002/api/saga/award-miles/'
        data = {
            'correlation_id': 'test-123',
            'booking_data': {'user_id': 1, 'flight_fare': 500.0}
        }
        response = requests.post(url, json=data, timeout=10)
        print(f"Loyalty SAGA: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Loyalty SAGA Error: {e}")

if __name__ == "__main__":
    test_services()
    test_payment_saga()
    test_loyalty_saga()