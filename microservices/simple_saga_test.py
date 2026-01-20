
"""
Simple SAGA Integration Test
Tests the basic SAGA endpoints to verify implementation
"""
import requests
import json

def test_individual_endpoints():
    """Test each SAGA endpoint individually"""
    print("🧪 Testing SAGA Implementation")
    print("=" * 50)
    
    # Test correlation ID
    correlation_id = "test-saga-123"
    
    # Test booking data
    booking_data = {
        "flight_id": 1,
        "user_id": 1,
        "passengers": [{"first_name": "John", "last_name": "Doe", "gender": "male"}],
        "contact_info": {"email": "john@test.com", "mobile": "1234567890"},
        "flight_fare": 500.0
    }
    
    endpoints = [
        {
            "name": "ReserveSeat",
            "url": "http://localhost:8001/api/saga/reserve-seat/",
            "description": "Reserve seat for booking"
        },
        {
            "name": "AuthorizePayment", 
            "url": "http://localhost:8003/api/saga/authorize-payment/",
            "description": "Authorize payment for booking"
        },
        {
            "name": "AwardMiles",
            "url": "http://localhost:8002/api/saga/award-miles/",
            "description": "Award loyalty miles"
        }
    ]
    
    print("📋 Testing SAGA Action Endpoints:")
    print("-" * 30)
    
    for endpoint in endpoints:
        print(f"\n🔄 Testing {endpoint['name']}...")
        print(f"   📍 {endpoint['description']}")
        
        try:
            payload = {
                "correlation_id": correlation_id,
                "booking_data": booking_data,
                "simulate_failure": False
            }
            
            response = requests.post(endpoint['url'], json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ SUCCESS - {endpoint['name']} completed")
                else:
                    print(f"   ❌ FAILED - {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP ERROR - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  CONNECTION ERROR - Service may not be running")
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
    
    print("\n📋 Testing SAGA Compensation Endpoints:")
    print("-" * 30)
    
    compensation_endpoints = [
        {
            "name": "ReverseMiles",
            "url": "http://localhost:8002/api/saga/reverse-miles/",
            "description": "Reverse awarded miles"
        },
        {
            "name": "CancelPayment",
            "url": "http://localhost:8003/api/saga/cancel-payment/",
            "description": "Cancel payment authorization"
        }
    ]
    
    for endpoint in compensation_endpoints:
        print(f"\n🔄 Testing {endpoint['name']}...")
        print(f"   📍 {endpoint['description']}")
        
        try:
            payload = {
                "correlation_id": correlation_id,
                "booking_data": booking_data
            }
            
            response = requests.post(endpoint['url'], json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ SUCCESS