#!/usr/bin/env python3
"""
Simple SAGA Test Script - Debug rollback issues
"""

import requests
import json
import time

def test_saga_rollback():
    """Test SAGA rollback functionality"""
    
    print("=== SAGA Rollback Test ===")
    
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
            "name": "Payment Failure Test",
            "params": {"simulate_authorizepayment_fail": True},
            "expected_compensations": 1
        },
        {
            "name": "Miles Award Failure Test", 
            "params": {"simulate_awardmiles_fail": True},
            "expected_compensations": 2
        },
        {
            "name": "Booking Confirmation Failure Test",
            "params": {"simulate_confirmbooking_fail": True},
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
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    print("ERROR: SAGA should have failed but succeeded")
                    print(f"Result: {result}")
                else:
                    print("SUCCESS: SAGA failed as expected")
                    print(f"Failed Step: {result.get('failed_step')}")
                    print(f"Error: {result.get('error')}")
                    
                    # Check compensation
                    compensation = result.get('compensation_result', {})
                    compensations_executed = compensation.get('successful_compensations', 0)
                    total_compensations = compensation.get('total_compensations', 0)
                    
                    print(f"Compensations: {compensations_executed}/{total_compensations}")
                    
                    if compensations_executed == scenario['expected_compensations']:
                        print("SUCCESS: Correct number of compensations executed")
                    else:
                        print(f"ERROR: Expected {scenario['expected_compensations']}, got {compensations_executed}")
                    
                    # Show compensation details
                    if compensation.get('results'):
                        print("Compensation Details:")
                        for comp in compensation['results']:
                            status = "SUCCESS" if comp.get('success') else "FAILED"
                            print(f"  {status} {comp.get('step')}: {comp.get('result', {}).get('message', 'No message')}")
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"REQUEST ERROR: {e}")
        
        print()
        time.sleep(1)  # Brief pause between tests

if __name__ == "__main__":
    test_saga_rollback()