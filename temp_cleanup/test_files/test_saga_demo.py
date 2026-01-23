#!/usr/bin/env python3
"""
SAGA Demo Test Script
Tests the complete SAGA failure and compensation flow
"""

import requests
import json
import time

def test_saga_failure_demo():
    """Test SAGA failure scenarios and compensation"""
    
    print("[SAGA] SAGA Failure Demo Test")
    print("=" * 50)
    
    # Test data
    booking_data = {
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
            "mobile": "1234567890",
            "email": "john.doe@example.com",
            "country_code": "1"
        }
    }
    
    # Test scenarios
    scenarios = [
        {
            "name": "Seat Reservation Failure",
            "params": {"simulate_reserveseat_fail": True},
            "expected_failure_step": "ReserveSeat",
            "expected_compensations": 0
        },
        {
            "name": "Payment Authorization Failure", 
            "params": {"simulate_authorizepayment_fail": True},
            "expected_failure_step": "AuthorizePayment",
            "expected_compensations": 1
        },
        {
            "name": "Miles Award Failure",
            "params": {"simulate_awardmiles_fail": True}, 
            "expected_failure_step": "AwardMiles",
            "expected_compensations": 2
        },
        {
            "name": "Booking Confirmation Failure",
            "params": {"simulate_confirmbooking_fail": True},
            "expected_failure_step": "ConfirmBooking", 
            "expected_compensations": 3
        }
    ]
    
    backend_url = "http://localhost:8001"
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[TEST {i}] {scenario['name']}")
        print("-" * 40)
        
        # Prepare test data with failure simulation
        test_data = {**booking_data, **scenario['params']}
        
        try:
            # Call SAGA booking endpoint
            response = requests.post(
                f"{backend_url}/api/saga/start-booking/",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    print("❌ UNEXPECTED: SAGA should have failed but succeeded")
                    print(f"   Result: {result}")
                else:
                    print("✅ EXPECTED: SAGA failed as expected")
                    print(f"   Failed Step: {result.get('failed_step')}")
                    print(f"   Error: {result.get('error')}")
                    
                    # Check compensation
                    compensation = result.get('compensation_result', {})
                    compensations_executed = compensation.get('successful_compensations', 0)
                    total_compensations = compensation.get('total_compensations', 0)
                    
                    print(f"   Compensations: {compensations_executed}/{total_compensations}")
                    
                    if compensations_executed == scenario['expected_compensations']:
                        print("✅ COMPENSATION: Correct number of compensations executed")
                    else:
                        print(f"❌ COMPENSATION: Expected {scenario['expected_compensations']}, got {compensations_executed}")
                    
                    # Show compensation details
                    if compensation.get('results'):
                        print("   Compensation Details:")
                        for comp in compensation['results']:
                            status = "✅" if comp.get('success') else "❌"
                            print(f"     {status} {comp.get('step')}: {comp.get('result', {}).get('message', 'No message')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST ERROR: {e}")
        
        print()
        time.sleep(1)  # Brief pause between tests
    
    print("🎯 SAGA Demo Summary")
    print("=" * 50)
    print("✅ Frontend: Toggle switches added to booking form")
    print("✅ Backend: SAGA orchestrator enhanced with failure simulation")
    print("✅ Loyalty: Compensation shows in point history with emojis")
    print("✅ Payment: Authorization cancellation with enhanced logging")
    print("✅ Booking: Cancelled bookings marked as CANCELLED_SAGA")
    print("✅ Logging: Enhanced compensation logging with emojis")
    print()
    print("🚀 Demo Instructions:")
    print("1. Go to http://localhost:8000")
    print("2. Search for flights and select one")
    print("3. Fill in passenger details")
    print("4. Check one of the SAGA Demo Control checkboxes")
    print("5. Submit booking to see SAGA failure and compensation")
    print("6. Check loyalty dashboard to see compensation transactions")
    print("7. Check bookings to see cancelled entries")

if __name__ == "__main__":
    test_saga_failure_demo()