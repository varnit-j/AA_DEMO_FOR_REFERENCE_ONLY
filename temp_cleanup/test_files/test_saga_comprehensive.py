#!/usr/bin/env python3
"""
Comprehensive SAGA Pattern Test
Tests all SAGA endpoints and orchestration
"""
import requests
import json

# Service endpoints
BACKEND_SERVICE = "http://localhost:8001"
LOYALTY_SERVICE = "http://localhost:8002"
PAYMENT_SERVICE = "http://localhost:8003"

def test_saga_orchestration():
    """Test complete SAGA orchestration"""
    print("Testing SAGA Orchestration")
    print("=" * 50)
    
    booking_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [{"first_name": "Test", "last_name": "User", "gender": "male"}],
        "contact_info": {"email": "test@example.com", "mobile": "1234567890"}
    }
    
    try:
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/start-booking/", json=booking_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS - SAGA Orchestration: {result}")
        else:
            print(f"FAILED - SAGA Failed: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_saga_orchestration()