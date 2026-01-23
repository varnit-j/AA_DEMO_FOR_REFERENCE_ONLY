#!/usr/bin/env python3
"""
Complete Integration Test Suite for AA Flight Booking Microservices
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_all_services():
    """Run comprehensive tests on all microservices"""
    
    base_urls = {
        'ui': 'http://localhost:8000',
        'backend': 'http://localhost:8001', 
        'loyalty': 'http://localhost:8002',
        'payment': 'http://localhost:8003'
    }
    
    session = requests.Session()
    results = []
    
    def log_test(name, success, message):
        status = "PASS" if success else "FAIL"
        print(f"{status} {name}: {message}")
        results.append({'test': name, 'success': success, 'message': message})
    
    print("STARTING COMPREHENSIVE MICROSERVICES INTEGRATION TESTS")
    print("="*60)
    
    # Test 1: Service Health Checks
    print("\nTesting Service Health...")
    services = [
        ('UI Service', base_urls['ui']),
        ('Backend Service', f"{base_urls['backend']}/api/flights/"),
        ('Loyalty Service', base_urls['loyalty']),
        ('Payment Service', base_urls['payment'])
    ]
    
    for name, url in services:
        try:
            response = session.get(url, timeout=10)
            if response.status_code in [200, 404]:
                log_test(f"{name} Health", True, f"Status: {response.status_code}")
            else:
                log_test(f"{name} Health", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test(f"{name} Health", False, f"Error: {str(e)}")
    
    # Test 2: Backend API Endpoints
    print("\nTesting Backend API Endpoints...")
    endpoints = [
        ('/api/flights/', 'Flight List API'),
        ('/api/places/', 'Places API')
    ]
    
    for endpoint, name in endpoints:
        try:
            url = f"{base_urls['backend']}{endpoint}"
            response = session.get(url)
            if response.status_code == 200:
                log_test(name, True, "API responding correctly")
            else:
                log_test(name, False, f"Status: {response.status_code}")
        except Exception as e:
            log_test(name, False, f"Error: {str(e)}")
    
    # Test 3: Flight Search Functionality
    print("\nTesting Flight Search...")
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        search_params = {
            'Origin': 'ORD',
            'Destination': 'DFW', 
            'DepartDate': tomorrow,
            'trip_type': '1',
            'seat': 'Economy'
        }
        
        search_url = f"{base_urls['ui']}/search"
        response = session.post(search_url, data=search_params)
        
        if response.status_code == 200:
            log_test("Flight Search", True, "Search functionality working")
        else:
            log_test("Flight Search", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Flight Search", False, f"Error: {str(e)}")
    
    # Test 4: User Interface Pages
    print("\nTesting UI Pages...")
    ui_pages = [
        ('/', 'Home Page'),
        ('/login', 'Login Page'),
        ('/register', 'Register Page'),
        ('/about', 'About Page'),
        ('/contact', 'Contact Page')
    ]
    
    for page, name in ui_pages:
        try:
            url = f"{base_urls['ui']}{page}"
            response = session.get(url)
            if response.status_code == 200:
                log_test(f"UI {name}", True, "Page loads successfully")
            else:
                log_test(f"UI {name}", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test(f"UI {name}", False, f"Error: {str(e)}")
    
    # Generate Final Report
    print("\n" + "="*60)
    print("FINAL TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} PASS")
    print(f"Failed: {failed_tests} FAIL")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\nFAILED TESTS:")
        for result in results:
            if not result['success']:
                print(f"  - {result['test']}: {result['message']}")
    
    print("\nPASSED TESTS:")
    for result in results:
        if result['success']:
            print(f"  - {result['test']}: {result['message']}")
    
    return passed_tests, failed_tests

if __name__ == "__main__":
    print("Starting AA Flight Booking Microservices Integration Tests...")
    passed, failed = test_all_services()
    
    if failed == 0:
        print("\nALL TESTS PASSED! System is ready for production.")
        exit(0)
    else:
        print(f"\n{failed} tests failed. Please review and fix issues.")
        exit(1)