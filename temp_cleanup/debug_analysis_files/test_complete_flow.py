#!/usr/bin/env python3.12
"""
Complete Flow Test - Tests all booking scenarios
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
sys.path.insert(0, str(Path(__file__).parent))

django.setup()

import logging
from flight.saga_orchestrator import BookingSAGAOrchestrator

logger = logging.getLogger(__name__)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_scenario(scenario_name, failure_scenarios=None):
    """Test a specific booking scenario"""
    print_section(f"SCENARIO: {scenario_name}")
    
    if failure_scenarios is None:
        failure_scenarios = {}
    
    # Create orchestrator
    orchestrator = BookingSAGAOrchestrator()
    
    # Prepare booking data
    booking_data = {
        'passenger_name': 'Test Passenger',
        'email': 'test@example.com',
        'flight_id': 1,
        'seat_class': 'economy',
        'phone': '555-1234'
    }
    
    # Execute SAGA
    print(f"Failure Scenarios: {failure_scenarios if failure_scenarios else 'None (Success Path)'}")
    result = orchestrator.start_booking_saga(booking_data, failure_scenarios)
    
    # Display results
    success = result.get('success', False)
    print(f"\nResult Status: {'[OK] SUCCESS' if success else '[FAIL] FAILED'}")
    print(f"Booking Reference: {result.get('booking_reference', result.get('correlation_id', 'N/A'))}")
    print(f"Failed Step: {result.get('failed_step', 'None')}")
    print(f"Error Message: {result.get('error', 'None')}")
    print(f"Steps Completed: {result.get('steps_completed', 0)}")
    
    # Verify expected results
    if failure_scenarios:
        assert not success, f"Expected failure but got success in {scenario_name}"
        print(f"\n[PASS] Test PASSED: Correctly failed and compensated")
    else:
        assert success, f"Expected success but got failure in {scenario_name}"
        print(f"\n[PASS] Test PASSED: All steps completed successfully")
    
    return result

def main():
    """Run complete flow tests"""
    print("\n" + "="*80)
    print("COMPLETE FLIGHT BOOKING FLOW TEST SUITE".center(80))
    print("="*80)
    
    results = {'scenarios': [], 'passed': 0, 'failed': 0}
    
    try:
        # TEST 1: Success Scenario
        print_section("TEST 1: NORMAL BOOKING FLOW (ALL STEPS SUCCESS)")
        result1 = test_scenario("Success Path - All Steps Complete", {})
        results['scenarios'].append({'name': 'Success Path', 'passed': result1.get('success', False)})
        if result1.get('success', False):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # TEST 2: Failure at Step 1
        print_section("TEST 2: FAILURE AT STEP 1 - RESERVE SEAT")
        result2 = test_scenario("Reserve Seat Failure", {'reserve_seat': True})
        results['scenarios'].append({'name': 'Reserve Seat Failure', 'passed': not result2.get('success', False)})
        if not result2.get('success', False):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # TEST 3: Failure at Step 2
        print_section("TEST 3: FAILURE AT STEP 2 - DEDUCT POINTS")
        result3 = test_scenario("Deduct Points Failure", {'deduct_loyalty_points': True})
        passed3 = not result3.get('success', False) and len(result3.get('compensation_history', [])) >= 1
        results['scenarios'].append({'name': 'Deduct Points Failure', 'passed': passed3})
        if passed3:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # TEST 4: Failure at Step 3
        print_section("TEST 4: FAILURE AT STEP 3 - PROCESS PAYMENT")
        result4 = test_scenario("Process Payment Failure", {'process_payment': True})
        passed4 = not result4.get('success', False) and len(result4.get('compensation_history', [])) >= 2
        results['scenarios'].append({'name': 'Payment Failure', 'passed': passed4})
        if passed4:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # TEST 5: Failure at Step 4
        print_section("TEST 5: FAILURE AT STEP 4 - CONFIRM BOOKING")
        result5 = test_scenario("Confirm Booking Failure", {'confirm_booking': True})
        passed5 = not result5.get('success', False) and len(result5.get('compensation_history', [])) >= 3
        results['scenarios'].append({'name': 'Confirm Booking Failure', 'passed': passed5})
        if passed5:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    print_section("COMPLETE FLOW TEST SUMMARY")
    print(f"Total Scenarios: {len(results['scenarios'])}")
    print(f"Passed: {results['passed']} [OK]")
    print(f"Failed: {results['failed']} [FAIL]")
    if len(results['scenarios']) > 0:
        print(f"Success Rate: {(results['passed']/len(results['scenarios'])*100):.1f}%\n")
    
    for scenario in results['scenarios']:
        status = "[OK] PASS" if scenario['passed'] else "[FAIL] FAIL"
        print(f"  {scenario['name']:.<50} {status}")
    
    print("\n" + "="*80)
    if results['failed'] == 0:
        print("[OK] ALL FLOW TESTS PASSED!")
    else:
        print(f"[FAIL] {results['failed']} TESTS FAILED")
    print("="*80 + "\n")
    
    return results['failed'] == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
