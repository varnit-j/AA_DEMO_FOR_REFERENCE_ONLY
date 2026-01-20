#!/usr/bin/env python3
"""
COMPREHENSIVE LOYALTY SYSTEM TEST SUITE
Senior Test Architect Level - Covers All Scenarios

This test suite validates:
1. Service connectivity and configuration
2. Points earning and redemption flows
3. Transaction history integrity
4. Error handling and edge cases
5. Integration between UI and loyalty services
6. Data consistency and persistence
"""

import requests
import json
import time
from datetime import datetime

class LoyaltyTestSuite:
    def __init__(self):
        self.services = {
            'ui': 'http://localhost:8000',
            'backend': 'http://localhost:8001', 
            'loyalty': 'http://localhost:8002',
            'payment': 'http://localhost:8003'
        }
        self.test_results = []
        self.failed_tests = []
        
    def log_result(self, test_name, passed, message="", details=None):
        """Log test result with detailed information"""
        status = "PASS" if passed else "FAIL"
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
        print(f"[{status}] {test_name}: {message}")
        if details:
            print(f"    Details: {details}")
    
    def test_service_architecture(self):
        """Test 1: Validate microservices architecture and connectivity"""
        print("\n" + "="*80)
        print("TEST SUITE 1: MICROSERVICES ARCHITECTURE VALIDATION")
        print("="*80)
        
        # Test each service individually
        for service_name, url in self.services.items():
            try:
                if service_name == 'loyalty':
                    response = requests.get(f"{url}/loyalty/status/", timeout=5)
                    expected_codes = [200]
                else:
                    response = requests.get(f"{url}/", timeout=5)
                    expected_codes = [200, 302, 404]  # Various valid responses
                
                if response.status_code in expected_codes:
                    self.log_result(f"Service-{service_name.upper()}", True, 
                                  f"Service accessible on {url}")
                else:
                    self.log_result(f"Service-{service_name.upper()}", False,
                                  f"Unexpected status {response.status_code}")
            except Exception as e:
                self.log_result(f"Service-{service_name.upper()}", False,
                              f"Service unreachable: {e}")
    
    def test_configuration_integrity(self):
        """Test 2: Critical configuration validation - catches misconfiguration bugs"""
        print("\n" + "="*80)
        print("TEST SUITE 2: CONFIGURATION INTEGRITY VALIDATION")
        print("="*80)
        
        # Test for service port misconfigurations
        misconfig_tests = [
            ("Loyalty on Payment Port", "http://localhost:8003/loyalty/status/"),
            ("Payment on Loyalty Port", "http://localhost:8002/payment/status/"),
            ("Backend on UI Port", "http://localhost:8000/api/flights/"),
        ]
        
        for test_name, wrong_url in misconfig_tests:
            try:
                response = requests.get(wrong_url, timeout=3)
                if response.status_code == 200:
                    self.log_result(f"Config-{test_name}", False,
                                  "CRITICAL: Service responding on wrong port!")
                else:
                    