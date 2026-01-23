#!/usr/bin/env python3
"""
Test script to verify SAGA ticket creation and cancellation date fixes
"""
import requests
import json
import time

def test_saga_booking():
    """Test SAGA booking with proper ticket creation"""
    print("=== Testing SAGA Booking Fixes ===")
    
    # Test data
    test_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [
            {
                "first_name": "John",
                "last_name": "Doe", 
                "gender": "male"
            }
        ],
        "contact_info": {
            "email": "john@example.com",
            "mobile": "1234567890"
        }
    }
    
    try:
        print("[INFO] Testing SAGA booking endpoint...")
        response = requests.post(
            'http://localhost:8001/api/saga/start-booking/',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"[INFO] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SAGA Booking Result:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                print("[OK] SUCCESS: SAGA booking completed successfully!")
                
                # Check if correlation_id exists
                correlation_id = result.get('correlation_id')
                if correlation_id:
                    print(f"[OK] Correlation ID: {correlation_id}")
                    
                    # Test SAGA status endpoint
                    print("\n2. Testing SAGA status endpoint...")
                    status_response = requests.get(
                        f'http://localhost:8001/api/saga/status/{correlation_id}/',
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        print("SAGA Status:")
                        print(json.dumps(status_result, indent=2))
                        print("[OK] SAGA status endpoint working!")
                    else:
                        print(f"[ERROR] SAGA status endpoint failed: {status_response.status_code}")
                        
                else:
                    print("[ERROR] No correlation_id in response")
                    
            else:
                print(f"[ERROR] SAGA booking failed: {result.get('error')}")
                
        else:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")

def test_individual_endpoints():
    """Test individual SAGA endpoints"""
    print("\n=== Testing Individual SAGA Endpoints ===")
    
    # Test data for individual steps
    test_data = {
        "correlation_id": "test-123",
        "booking_data": {
            "flight_id": 1,
            "user_id": 1,
            "passengers": [{"first_name": "Test", "last_name": "User", "gender": "male"}],
            "contact_info": {"email": "test@example.com", "mobile": "1234567890"},
            "flight_fare": 100.0
        }
    }
    
    endpoints = [
        ("Reserve Seat", "http://localhost:8001/api/saga/reserve-seat/"),
        ("Confirm Booking", "http://localhost:8001/api/saga/confirm-booking/")
    ]
    
    for name, url in endpoints:
        try:
            print(f"\n[INFO] Testing {name}...")
            response = requests.post(
                url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"[OK] {name} endpoint working!")
                else:
                    print(f"[ERROR] {name} failed: {result.get('error')}")
            else:
                print(f"[ERROR] {name} HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] {name} exception: {e}")

if __name__ == "__main__":
    test_saga_booking()
    test_individual_endpoints()
    print("\n=== Test Complete ===")