
"""
Quick SAGA Integration Test
Tests basic connectivity and SAGA endpoints
"""
import requests
import json

def test_services():
    """Test if all services are running and SAGA endpoints work"""
    print("🧪 Quick SAGA Integration Test")
    print("=" * 50)
    
    # Test service health
    services = [
        ("Backend", "http://localhost:8001/api/health/"),
        ("Loyalty", "http://localhost:8002/api/loyalty/"),
        ("Payment", "http://localhost:8003/health/")
    ]
    
    print("\n🏥 Service Health Check:")
    all_healthy = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {name} Service - HEALTHY")
            else:
                print(f"   ❌ {name} Service - Status: {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"   ❌ {name} Service - ERROR: {str(e)[:50]}")
            all_healthy = False
    
    if not all_healthy:
        print("\n⚠️  Some services are not running. Please start all services first.")
        return False
    
    # Test SAGA endpoints
    print("\n🔄 SAGA Endpoints Test:")
    correlation_id = "test-123"
    test_data = {
        "correlation_id": correlation_id,
        "booking_data": {
            "flight_id": 1,
            "user_id": 1,
            "passengers": [{"first_name": "John", "last_name": "Doe", "gender": "male"}],
            "contact_info": {"email": "test@test.com", "mobile": "1234567890"},
            "flight_fare": 500.0
        },
        "simulate_failure": False
    }
    
    # Test individual SAGA steps
    saga_tests = [
        ("ReserveSeat", "http://localhost:8001/api/saga/reserve-seat/"),
        ("AuthorizePayment", "http://localhost:8003/api/saga/authorize-payment/"),
        ("AwardMiles", "http://localhost:8002/api/saga/award-miles/")
    ]
    
    saga_working = True
    for step_name, url in saga_tests:
        try:
            response = requests.post(url, json=test_data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {step_name} - SUCCESS")
                else:
                    print(f"   ❌ {step_name} - FAILED: {result.get('error', 'Unknown')}")
                    saga_working = False
            else:
                print(f"   ❌ {step_name} - HTTP {response.status_code}")
                saga_working = False
        except Exception as e:
            print(f"   ❌ {step_name} - ERROR: {str(e)[:50]}")
            saga_working = False
    
    # Test compensation endpoints
    print("\n🔄 Compensation Endpoints Test:")
    comp_data = {"correlation_id": correlation_id, "booking_data": test_data["booking_data"]}
    
    comp_tests = [
        ("ReverseMiles", "http://localhost:8002/api/saga/reverse-miles/"),
        ("CancelPayment", "http://localhost:8003/api/saga/cancel-payment/")
    ]
    
    for step_name, url in comp_tests:
        try:
            response = requests.post(url, json=comp_data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {step_name} - SUCCESS")
                else:
                    print(f"   ❌ {step_name} - FAILED: {result.get('error', 'Unknown')}")
            else:
                print(f"   ❌ {step_name} - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {step_name} - ERROR: {str(e)[:50]}")
    
    print(f"\n📊 Summary:")
    print(f"   Services Health: {'✅ PASS' if all_healthy else '❌ FAIL'}")
    print(f"   SAGA Endpoints: {'✅ PASS' if saga_working else '❌ FAIL'}")
    
    return all_healthy and saga_working

if __name__ == "__main__":
    test_services()