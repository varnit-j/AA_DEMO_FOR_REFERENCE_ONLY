#!/usr/bin/env python3
"""
Test script to verify SAGA status display fix
Tests different failure types to ensure correct status information is shown
"""

import requests
import re
from urllib.parse import urlencode

def test_saga_status_display():
    """Test that different failure types show correct status information"""
    
    base_url = "http://localhost:8000/saga/results"
    
    # Test cases for different failure scenarios
    test_cases = [
        {
            'name': 'ReserveSeat Failure',
            'params': {'correlation_id': 'test-001', 'demo': 'true', 'failure_type': 'reserveseat'},
            'expected_failed_step': 'ReserveSeat',
            'expected_steps_completed': '0',
            'expected_compensations': '0'
        },
        {
            'name': 'AuthorizePayment Failure', 
            'params': {'correlation_id': 'test-002', 'demo': 'true', 'failure_type': 'authorizepayment'},
            'expected_failed_step': 'AuthorizePayment',
            'expected_steps_completed': '1',
            'expected_compensations': '1'
        },
        {
            'name': 'AwardMiles Failure',
            'params': {'correlation_id': 'test-003', 'demo': 'true', 'failure_type': 'awardmiles'},
            'expected_failed_step': 'AwardMiles', 
            'expected_steps_completed': '2',
            'expected_compensations': '2'
        },
        {
            'name': 'ConfirmBooking Failure',
            'params': {'correlation_id': 'test-004', 'demo': 'true', 'failure_type': 'confirmbooking'},
            'expected_failed_step': 'ConfirmBooking',
            'expected_steps_completed': '3', 
            'expected_compensations': '3'
        }
    ]
    
    print("[TEST] Testing SAGA Status Display Fix")
    print("=" * 50)
    
    results = []
    
    for test_case in test_cases:
        print(f"\n[TEST] Testing: {test_case['name']}")
        
        # Build URL with parameters
        url = f"{base_url}?{urlencode(test_case['params'])}"
        print(f"[URL] {url}")
        
        try:
            # Make request
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Extract status information from HTML
                failed_step_match = re.search(r'Failed at (\w+)', html_content)
                steps_completed_match = re.search(r'<strong>Steps Completed:</strong>\s*(\d+)/4', html_content)
                compensations_match = re.search(r'<strong>Compensations:</strong>\s*(\d+)\s+executed successfully', html_content)
                
                # Check results
                test_result = {
                    'name': test_case['name'],
                    'url': url,
                    'status': 'PASS',
                    'issues': []
                }
                
                # Verify failed step
                if failed_step_match:
                    actual_failed_step = failed_step_match.group(1)
                    if actual_failed_step != test_case['expected_failed_step']:
                        test_result['status'] = 'FAIL'
                        test_result['issues'].append(f"Failed step: expected '{test_case['expected_failed_step']}', got '{actual_failed_step}'")
                    else:
                        print(f"[OK] Failed step: {actual_failed_step}")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['issues'].append("Failed step not found in HTML")
                
                # Verify steps completed
                if steps_completed_match:
                    actual_steps = steps_completed_match.group(1)
                    if actual_steps != test_case['expected_steps_completed']:
                        test_result['status'] = 'FAIL'
                        test_result['issues'].append(f"Steps completed: expected '{test_case['expected_steps_completed']}', got '{actual_steps}'")
                    else:
                        print(f"[OK] Steps completed: {actual_steps}/4")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['issues'].append("Steps completed not found in HTML")
                
                # Verify compensations
                if compensations_match:
                    actual_compensations = compensations_match.group(1)
                    if actual_compensations != test_case['expected_compensations']:
                        test_result['status'] = 'FAIL'
                        test_result['issues'].append(f"Compensations: expected '{test_case['expected_compensations']}', got '{actual_compensations}'")
                    else:
                        print(f"[OK] Compensations: {actual_compensations} executed")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['issues'].append("Compensations not found in HTML")
                
                # Print result
                if test_result['status'] == 'PASS':
                    print(f"[PASS] {test_case['name']}: PASSED")
                else:
                    print(f"[FAIL] {test_case['name']}: FAILED")
                    for issue in test_result['issues']:
                        print(f"   - {issue}")
                
            else:
                test_result = {
                    'name': test_case['name'],
                    'url': url,
                    'status': 'FAIL',
                    'issues': [f"HTTP {response.status_code}: {response.reason}"]
                }
                print(f"[FAIL] {test_case['name']}: HTTP ERROR {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            test_result = {
                'name': test_case['name'],
                'url': url,
                'status': 'FAIL',
                'issues': [f"Request failed: {str(e)}"]
            }
            print(f"[FAIL] {test_case['name']}: REQUEST FAILED - {str(e)}")
        
        results.append(test_result)
    
    # Summary
    print("\n" + "=" * 50)
    print("[SUMMARY] TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    print(f"[OK] Passed: {passed}/{total}")
    print(f"[FAIL] Failed: {total - passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED! SAGA status display fix is working correctly.")
        return True
    else:
        print("[WARNING] Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    test_saga_status_display()