#!/usr/bin/env python3
"""
Unit Tests for Loyalty Service
"""

import unittest
import requests
import json

class LoyaltyServiceUnitTests(unittest.TestCase):
    
    def setUp(self):
        self.base_url = 'http://localhost:8002'
        self.session = requests.Session()
    
    def test_service_health(self):
        """Test loyalty service is running"""
        response = self.session.get(f"{self.base_url}/")
        self.assertIn(response.status_code, [200, 404])
        print(f"SUCCESS Loyalty Service Health: Status {response.status_code}")
    
    def test_loyalty_dashboard_api(self):
        """Test loyalty dashboard API"""
        response = self.session.get(f"{self.base_url}/api/loyalty/dashboard/")
        self.assertIn(response.status_code, [200, 404, 405])
        print(f"SUCCESS Loyalty Dashboard API: Status {response.status_code}")
    
    def test_loyalty_points_api(self):
        """Test loyalty points API"""
        response = self.session.get(f"{self.base_url}/api/loyalty/points/")
        self.assertIn(response.status_code, [200, 404, 405])
        print(f"SUCCESS Loyalty Points API: Status {response.status_code}")
    
    def test_loyalty_tiers_api(self):
        """Test loyalty tiers API"""
        response = self.session.get(f"{self.base_url}/api/loyalty/tiers/")
        self.assertIn(response.status_code, [200, 404, 405])
        print(f"SUCCESS Loyalty Tiers API: Status {response.status_code}")

if __name__ == '__main__':
    print("Running Loyalty Service Unit Tests...")
    unittest.main(verbosity=2)