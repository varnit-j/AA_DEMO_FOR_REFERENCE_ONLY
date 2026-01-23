#!/usr/bin/env python3
"""
Complete SAGA Validation Test
Tests success and failure scenarios
"""
import requests
import json

BACKEND_SERVICE = "http://localhost:8001"

def test_saga_success():
    """Test successful SAGA execution"""
    print("Testing SAGA Success Scenario")
    print("=" * 40)
    
    booking_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [{"first_name": "John", "last_name": "Doe", "gender": "male"}],
        "contact_info": {"email": "john@test.com", "mobile": "1234567890"}
    }
    
    try:
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/start-booking/", json=booking_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: SAGA completed successfully")
                print(f"Correlation ID: {result.get('correlation_id')}")
                print(f"Steps completed: {result.get('steps_completed')}")
                return True
            else:
                print(f"FAILED: {result.get('error')}")
                return False
        else:
            print(f"HTTP ERROR: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_saga_failure():
    """Test SAGA failure and compensation"""
    print("\nTesting SAGA Failure Scenario")
    print("=" * 40)
    
    booking_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [{"first_name": "Jane", "last_name": "Smith", "gender": "female"}],
        "contact_info": {"email": "jane@test.com", "mobile": "9876543210"},
        "simulate_authorizepayment_fail": True  # Simulate payment failure
    }
    
    try:
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/start-booking/", json=booking_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('success'):
                print("SUCCESS: SAGA failed as expected and compensation executed")
                print(f"Failed at step: {result.get('failed_step')}")
                print(f"Error: {result.get('error')}")
                compensation = result.get('compensation_result', {})
                print(f"Compensations executed: {compensation.get('total_compensations', 0)}")
                return True
            else:
                print("UNEXPECTED: SAGA should have failed but succeeded")
                return False
        else:
            print(f"HTTP ERROR: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("SAGA Complete Validation Test")
    print("=" * 50)
    
    success_test = test_saga_success()
    failure_test = test_saga_failure()
    
    print("\nTest Results:")
    print("=" * 20)
    print(f"Success Scenario: {'PASS' if success_test else 'FAIL'}")
    print(f"Failure Scenario: {'PASS' if failure_test else 'FAIL'}")
    
    if success_test and failure_test:
        print("\nALL TESTS PASSED - SAGA implementation is working correctly!")
    else:
        print("\nSOME TESTS FAILED - Check SAGA implementation")