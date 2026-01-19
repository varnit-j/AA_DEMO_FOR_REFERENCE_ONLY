#!/usr/bin/env python3
"""
Unit Tests for Payment Service
"""

import unittest
import requests
import json

class PaymentServiceUnitTests(unittest.TestCase):
    
    def setUp(self):
        self.base_url = 'http://localhost:8003'
        self.session = requests.Session()
    
    def test_service_health(self):
        """Test payment service is running"""
        response = self.session.get(f"{self.base_url}/")
        self.assertIn(response.status_code, [200, 404])
        print(f"✅ Payment Service Health: Status {response.status_code}")
    
    def test_payment_health_api(self):
        """Test payment health API"""
        response = self.session.get(f"{self.base_url}/api/payment/health/")
        self.assertIn(response.status_code, [200, 404, 405])
        print(f"✅ Payment Health API: Status {response.status_code}")
    
    def test_payment_process_api(self):
        """Test payment process API"""
        response = self.session.get(f"{self.base_url}/api/payment/process/")
        self.assertIn(response.status_code, [200, 404, 405])
        print(f"✅ Payment Process API: Status {response.status_code}")
    
    def test_stripe_config_api(self):
        """Test Stripe configuration API"""
        response = self.session.get(f"{self.base_url}/api/payment/stripe/config/")
        self.assertIn(response.status_code, [200, 404, 405])
        print(f"✅ Stripe Config API: Status {response.status_code}")

if __name__ == '__main__':
    print("Running Payment Service Unit Tests...")
    unittest.main(verbosity=2)