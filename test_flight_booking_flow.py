#!/usr/bin/env python3
"""
Comprehensive Flight Booking System Test Script
Tests the complete flow from registration to payment for AAdvantage program
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Service URLs
UI_SERVICE = "http://localhost:8203"
BACKEND_SERVICE = "http://localhost:8200"
LOYALTY_SERVICE = "http://localhost:8202"
PAYMENT_SERVICE = "http://localhost:8201"

class FlightBookingTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.booking_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'data': data
        })
        
    def test_service_health(self):
        """Test if all services are running"""
        print("\n🔍 Testing Service Health...")
        
        services = [
            ("UI Service", UI_SERVICE),
            ("Loyalty Service", f"{LOYALTY_SERVICE}/api/loyalty/"),
        ]
        
        for name, url in services:
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    self.log_test(f"{name} Health", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"{name} Health", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{name} Health", False, f"Error: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n👤 Testing User Registration...")
        
        # Test data for AAdvantage member
        test_user = {
            'username': f'testuser_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'TestPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890'
        }
        
        try:
            # Try to register via UI service
            response = self.session.post(f"{UI_SERVICE}/register/", data=test_user)
            
            if response.status_code in [200, 201, 302]:  # 302 for redirect after successful registration
                self.log_test("User Registration", True, f"User {test_user['username']} registered successfully")
                return test_user
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return None
    
    def test_user_login(self, user_data):
        """Test user login"""
        print("\n🔐 Testing User Login...")
        
        if not user_data:
            self.log_test("User Login", False, "No user data available")
            return False
            
        try:
            login_data = {
                'username': user_data['username'],
                'password': user_data['password']
            }
            
            response = self.session.post(f"{UI_SERVICE}/login/", data=login_data)
            
            if response.status_code in [200, 302]:
                self.log_test("User Login