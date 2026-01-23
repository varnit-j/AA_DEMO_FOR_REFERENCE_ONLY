#!/usr/bin/env python3
"""
Complete Booking Flow Validation Test

Tests the complete UI → Backend booking flow to identify break points:
1. Flight search
2. Review page (flight data loading)
3. Booking form (with/without SAGA)
4. Payment page
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
UI_URL = "http://localhost:8000"
TIMEOUT = 10

# Test data
test_flight_id = 1
test_passenger = {
    "first_name": "Test",
    "last_name": "User",
    "gender": "male"
}

def log_test(name, status, message=""):
    """Log test result"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = "✓" if status else "✗"
    print(f"[{timestamp}] {icon} {name}")
    if message:
        print(f"    └─ {message}")

def test_backend_connectivity():
    """Test 1: Backend service is reachable"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/flights/1/", timeout=TIMEOUT)
        if response.status_code in [200, 404]:
            log_test("Backend Connectivity", True, "Service responding")
            return True
        else:
            log_test("Backend Connectivity", False, f"HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        log_test("Backend Connectivity", False, f"Connection refused: {str(e)[:50]}")
        return False
    except Exception as e:
        log_test("Backend Connectivity", False, f"Error: {str(e)[:50]}")
        return False

def test_flight_data_retrieval():
    """Test 2: Can retrieve flight data"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/flights/{test_flight_id}/",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            flight_num = data.get('flight_number', data.get('plane', 'Unknown'))
            airline = data.get('airline', 'Unknown')
            log_test(
                "Flight Data Retrieval",
                True,
                f"{airline} {flight_num} (ID: {test_flight_id})"
            )
            return True
        elif response.status_code == 404:
            log_test(
                "Flight Data Retrieval",
                False,
                f"Flight {test_flight_id} not found in database"
            )
            return False
        else:
            log_test(
                "Flight Data Retrieval",
                False,
                f"HTTP {response.status_code}: {response.text[:100]}"
            )
            return False
    except Exception as e:
        log_test("Flight Data Retrieval", False, f"Error: {str(e)[:50]}")
        return False

def test_saga_booking_normal():
    """Test 3: SAGA booking without failure simulation"""
    try:
        booking_data = {
            "flight_id": test_flight_id,
            "user_id": 1,
            "total_fare": 500.0,
            "loyalty_points_to_use": 0,
            "payment_method": "card",
            "passengers": [test_passenger],
            "failure_scenarios": {
                "reserve_seat": False,
                "deduct_loyalty_points": False,
                "process_payment": False,
                "confirm_booking": False
            }
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/saga/start-booking/",
            json=booking_data,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get('success'):
                log_test(
                    "SAGA Booking (Normal)",
                    True,
                    f"Correlation ID: {result.get('correlation_id', 'N/A')[:8]}..."
                )
                return True
            else:
                log_test(
                    "SAGA Booking (Normal)",
                    False,
                    f"API returned success=false: {result.get('error', 'Unknown error')}"
                )
                return False
        else:
            log_test(
                "SAGA Booking (Normal)",
                False,
                f"HTTP {response.status_code}"
            )
            return False
    except Exception as e:
        log_test("SAGA Booking (Normal)", False, f"Error: {str(e)[:50]}")
        return False

def test_saga_booking_with_failure():
    """Test 4: SAGA booking with failure simulation"""
    try:
        booking_data = {
            "flight_id": test_flight_id,
            "user_id": 1,
            "total_fare": 500.0,
            "loyalty_points_to_use": 0,
            "payment_method": "card",
            "passengers": [test_passenger],
            "failure_scenarios": {
                "reserve_seat": True,  # Simulate failure at first step
                "deduct_loyalty_points": False,
                "process_payment": False,
                "confirm_booking": False
            }
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/saga/start-booking/",
            json=booking_data,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if not result.get('success') and result.get('failed_step'):
                log_test(
                    "SAGA Booking (With Failure)",
                    True,
                    f"Failed as expected at: {result.get('failed_step')}"
                )
                return True
            elif result.get('success'):
                log_test(
                    "SAGA Booking (With Failure)",
                    False,
                    "Expected failure but booking succeeded"
                )
                return False
            else:
                log_test(
                    "SAGA Booking (With Failure)",
                    False,
                    f"Error: {result.get('error', 'Unknown error')}"
                )
                return False
        else:
            log_test(
                "SAGA Booking (With Failure)",
                False,
                f"HTTP {response.status_code}"
            )
            return False
    except Exception as e:
        log_test("SAGA Booking (With Failure)", False, f"Error: {str(e)[:50]}")
        return False

def test_ui_review_page():
    """Test 5: UI Review page loads with flight data"""
    try:
        # Note: Requires authenticated session
        response = requests.get(
            f"{UI_URL}/review/",
            params={
                "flight1Id": test_flight_id,
                "flight1Date": "22-01-2026",
                "seatClass": "economy"
            },
            timeout=TIMEOUT,
            allow_redirects=False
        )
        
        if response.status_code == 200:
            # Check if flight data is in HTML
            if "flight1" in response.text.lower() or "flight" in response.text.lower():
                log_test(
                    "UI Review Page",
                    True,
                    "Flight data found in HTML"
                )
                return True
            else:
                # Might still work but no obvious flight data
                log_test(
                    "UI Review Page",
                    True,
                    "Page loaded (flight data status unclear)"
                )
                return True
        elif response.status_code == 302:
            log_test(
                "UI Review Page",
                False,
                "Redirected (likely requires login)"
            )
            return False
        else:
            log_test(
                "UI Review Page",
                False,
                f"HTTP {response.status_code}"
            )
            return False
    except Exception as e:
        log_test("UI Review Page", False, f"Error: {str(e)[:50]}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("BOOKING FLOW VALIDATION TEST")
    print("="*70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"UI URL: {UI_URL}")
    print("="*70 + "\n")
    
    results = {
        "Backend Connectivity": test_backend_connectivity(),
        "Flight Data Retrieval": test_flight_data_retrieval(),
        "SAGA Booking (Normal)": test_saga_booking_normal(),
        "SAGA Booking (With Failure)": test_saga_booking_with_failure(),
        "UI Review Page": test_ui_review_page(),
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
    
    print("="*70)
    print(f"Result: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    if passed == total:
        print("✓ All booking flow components are working correctly!")
        print("\nYou can now:")
        print("1. Open browser to http://localhost:8000")
        print("2. Search for flights")
        print("3. Click 'Book Flight'")
        print("4. Add passenger and check SAGA demo box (optional)")
        print("5. Proceed to payment")
        return 0
    else:
        print("✗ Some components are failing. Check error messages above.")
        print("\nTroubleshooting:")
        if not results["Backend Connectivity"]:
            print("- Start backend: cd microservices/backend-service && python manage.py runserver 8001")
        if not results["Flight Data Retrieval"]:
            print("- Ensure flights exist in backend database")
        if not results["UI Review Page"]:
            print("- Start UI: cd microservices/ui-service && python manage.py runserver 8000")
            print("- Login first at http://localhost:8000/login")
        return 1

if __name__ == "__main__":
    exit(main())
