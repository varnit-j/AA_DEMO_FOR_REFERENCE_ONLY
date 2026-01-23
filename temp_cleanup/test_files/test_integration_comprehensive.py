#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Points Redemption Flow
This test suite validates the complete integration between UI service and loyalty service
including configuration validation, end-to-end flows, and error scenarios.

Created to catch configuration errors and integration issues that unit tests miss.
"""

import requests
import json
import time
from datetime import datetime

# Service configurations
SERVICES = {
    'ui': 'http://localhost:8000',
    'backend': 'http://localhost:8001', 
    'loyalty': 'http://localhost:8002',
    'payment': 'http://localhost:8003'
}

class IntegrationTestSuite:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, passed, message="", details=None):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        if not passed:
            self.failed_tests.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"    Details: {details}")
    
    def test_service_connectivity(self):
        """Test 1: Validate all services are running and accessible"""
        print("\n" + "="*60)
        print("TEST SUITE 1: SERVICE CONNECTIVITY")
        print("="*60)
        
        for service_name, url in SERVICES.items():
            try:
                response = requests.get(f"{url}/", timeout=5)
                if response.status_code in [200, 302]:  # 302 for redirects
                    self.log_test(f"Service Connectivity - {service_name}", True, 
                                f"Service online at {url}")
                else:
                    self.log_test(f"Service Connectivity - {service_name}", False,
                                f"Unexpected status {response.status_code}")
            except Exception as e:
                self.log_test(f"Service Connectivity - {service_name}", False,
                            f"Service offline: {e}")
    
    def test_loyalty_service_endpoints(self):
        """Test 2: Validate loyalty service API endpoints"""
        print("\n" + "="*60)
        print("TEST SUITE 2: LOYALTY SERVICE API VALIDATION")
        print("="*60)
        
        # Test loyalty status endpoint
        try:
            response = requests.get(f"{SERVICES['loyalty']}/loyalty/status/", timeout=5)
            if response.status_code == 200:
                self.log_test("Loyalty API - Status Endpoint", True, "Status endpoint accessible")
            else:
                self.log_test("Loyalty API - Status Endpoint", False, 
                            f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Loyalty API - Status Endpoint", False, f"Error: {e}")
        
        # Test points addition endpoint
        test_data = {
            'user_id': 'test_integration',
            'amount': 100.0,
            'transaction_id': f'TEST_ADD_{int(time.time())}'
        }
        try:
            response = requests.post(f"{SERVICES['loyalty']}/loyalty/add-points/", 
                                   json=test_data, timeout=10)
            if response.status_code == 200:
                self.log_test("Loyalty API - Add Points", True, "Points addition works")
            else:
                self.log_test("Loyalty API - Ad