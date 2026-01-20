
"""
Test Script for SAGA Pattern Implementation
Demonstrates the flight booking SAGA flow with success and failure scenarios
"""
import requests
import json
import time

# Service endpoints
BACKEND_SERVICE = "http://localhost:8001"
LOYALTY_SERVICE = "http://localhost:8002"
PAYMENT_SERVICE = "http://localhost:8003"

def test_saga_endpoints():
    """Test individual SAGA endpoints"""
    print("=== Testing SAGA Endpoints ===")
    
    # Test data
    test_correlation_id = "test-12345"
    test_booking_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [
            {"first_name": "John", "last_name": "Doe", "gender": "male"}
        ],
        "contact_info": {
            "email": "john@example.com",
            "mobile": "+1234567890"
        },
        "flight_fare": 500.0
    }
    
    # Test 1: Reserve Seat
    print("\n1. Testing ReserveSeat...")
    try:
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/reserve-seat/", json={
            "correlation_id": test_correlation_id,
            "booking_data": test_booking_data,
            "simulate_failure": False
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Authorize Payment
    print("\n2. Testing AuthorizePayment...")
    try:
        response = requests.post(f"{PAYMENT_SERVICE}/api/saga/authorize-payment/", json={
            "correlation_id": test_correlation_id,
            "booking_data": test_booking_data,
            "simulate_failure": False
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Award Miles
    print("\n3. Testing AwardMiles...")
    try:
        response = requests.post(f"{LOYALTY_SERVICE}/api/saga/award-miles/", json={
            "correlation_id": test_correlation_id,
            "booking_data": test_booking_data,
            "simulate_failure": False
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Testing Compensation Endpoints ===")
    
    # Test 4: Reverse Miles (Compensation)
    print("\n4. Testing ReverseMiles...")
    try:
        response = requests.post(f"{LOYALTY_SERVICE}/api/saga/reverse-miles/", json={
            "correlation_id": test_correlation_id,
            "booking_data": test_booking_data
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Cancel Payment (Compensation)
    print("\n5. Testing CancelPayment...")
    try:
        response = requests.post(f"{PAYMENT_SERVICE}/api/saga/cancel-payment/", json={
            "correlation_id": test_correlation_id,
            "booking_data": test_booking_data
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_saga_endpoints()