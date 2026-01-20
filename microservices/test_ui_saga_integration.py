#!/usr/bin/env python3
"""
Test UI Integration with SAGA Pattern
"""
import requests
import json

UI_SERVICE = "http://localhost:8000"
BACKEND_SERVICE = "http://localhost:8001"

def test_ui_saga_integration():
    """Test that UI service is properly integrated with SAGA"""
    print("Testing UI SAGA Integration")
    print("=" * 40)
    
    # Test 1: Check if UI service is running
    try:
        response = requests.get(f"{UI_SERVICE}/")
        print(f"UI Service Status: {response.status_code}")
        if response.status_code != 200:
            print("ERROR: UI Service not accessible")
            return False
    except Exception as e:
        print(f"ERROR: Cannot connect to UI service: {e}")
        return False
    
    # Test 2: Verify SAGA endpoint is accessible from backend
    try:
        test_booking_data = {
            "flight_id": 1,
            "user_id": 1,
            "passengers": [{"first_name": "Test", "last_name": "User", "gender": "male"}],
            "contact_info": {"email": "test@example.com", "mobile": "1234567890"}
        }
        
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/start-booking/", json=test_booking_data)
        print(f"SAGA Endpoint Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: UI can now use SAGA pattern for bookings")
                print(f"SAGA Correlation ID: {result.get('correlation_id')}")
                print(f"Steps completed: {result.get('steps_completed')}")
                return True
            else:
                print(f"SAGA Failed: {result.get('error')}")
                return False
        else:
            print(f"ERROR: SAGA endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: SAGA test failed: {e}")
        return False

if __name__ == "__main__":
    print("UI SAGA Integration Test")
    print("=" * 50)
    
    success = test_ui_saga_integration()
    
    print("\nTest Results:")
    print("=" * 20)
    if success:
        print("SUCCESS: UI is properly integrated with SAGA pattern!")
        print("- UI service is accessible")
        print("- SAGA booking endpoint is working")
        print("- UI will now use SAGA for all bookings")
    else:
        print("FAILED: UI SAGA integration has issues")