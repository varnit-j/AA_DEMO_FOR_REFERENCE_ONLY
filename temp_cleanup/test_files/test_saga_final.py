#!/usr/bin/env python3
"""
Final test to verify SAGA booking works end-to-end
"""
import requests
import json

def test_saga_booking():
    """Test SAGA booking with proper data"""
    print("=== Final SAGA Booking Test ===")
    
    # Test data
    test_data = {
        "flight_id": 13850,
        "user_id": 1,
        "passengers": [
            {
                "first_name": "John",
                "last_name": "Doe",
                "gender": "male"
            }
        ],
        "contact_info": {
            "email": "john.doe@example.com",
            "mobile": "1234567890"
        }
    }
    
    try:
        print("1. Testing SAGA booking endpoint...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            'http://localhost:8001/api/saga/start-booking/',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("SAGA Booking Result:")
                print(json.dumps(result, indent=2))
                
                if result.get('success'):
                    print("✅ SUCCESS: SAGA booking completed successfully!")
                    print(f"✅ Booking Reference: {result.get('booking_reference', 'N/A')}")
                    print(f"✅ Correlation ID: {result.get('correlation_id', 'N/A')}")
                    print("✅ User should now be redirected to payment page!")
                    return True
                else:
                    print(f"❌ SAGA booking failed: {result.get('error')}")
                    if 'failed_step' in result:
                        print(f"❌ Failed at step: {result['failed_step']}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_saga_booking()
    if success:
        print("\n🎉 SAGA booking is working! Payment redirect should work now.")
    else:
        print("\n💥 SAGA booking still has issues.")