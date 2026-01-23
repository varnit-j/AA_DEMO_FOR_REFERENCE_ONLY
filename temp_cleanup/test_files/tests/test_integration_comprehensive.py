#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for AA Flight Booking System
Tests the complete flight booking flow across all microservices
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta

class FlightBookingIntegrationTest:
    def __init__(self):
        self.base_urls = {
            'ui': 'http://localhost:8000',
            'backend': 'http://localhost:8001', 
            'loyalty': 'http://localhost:8002',
            'payment': 'http://localhost:8003'
        }
        self.session = requests.Session()
        self.test_results = []
        self.test_user = None
        self.booking_data = {}
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results with detailed information"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'data': data,
            'timestamp': timestamp
        })
        
        if not success:
            print(f"   ERROR DETAILS: {data}")

    def test_service_health(self):
        """Test if all microservices are running and responding"""
        print("\n🔍 TESTING SERVICE HEALTH...")
        
        services = [
            ('UI Service', self.base_urls['ui']),
            ('Backend Service', f"{self.base_urls['backend']}/api/health/"),
            ('Loyalty Service', f"{self.base_urls['loyalty']}/api/health/"),
            ('Payment Service', f"{self.base_urls['payment']}/api/health/")
        ]
        
        all_healthy = True
        for name, url in services:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code in [200, 404]:  # 404 is OK for basic health check
                    self.log_test(f"{name} Health", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"{name} Health", False, f"Status: {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.log_test(f"{name} Health", False, f"Connection Error: {str(e)}")
                all_healthy = False
                
        return all_healthy

    def test_user_registration_and_login(self):
        """Test user registration and login flow"""
        print("\n👤 TESTING USER REGISTRATION & LOGIN...")
        
        # Generate unique test user
        timestamp = int(time.time())
        self.test_user = {
            'username': f'testuser_{timestamp}',
            'email': f'test_{timestamp}@example.com',
            'password': 'TestPass123!',
            'firstname': 'Test',
            'lastname': 'User'
        }
        
        try:
            # Test registration
            register_url = f"{self.base_urls['ui']}/register"
            response = self.session.post(register_url, data=self.test_user)
            
            if response.status_code in [200, 201, 302]:
                self.log_test("User Registration", True, f"User {self.test_user['username']} registered")
                
                # Test login
                login_data = {
                    'username': self.test_user['username'],
                    'password': self.test_user['password']
                }
                
                login_url = f"{self.base_urls['