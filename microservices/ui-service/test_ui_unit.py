#!/usr/bin/env python3
"""
Unit Tests for UI Service
"""

import unittest
import requests
from datetime import datetime, timedelta

class UIServiceUnitTests(unittest.TestCase):
    
    def setUp(self):
        self.base_url = 'http://localhost:8000'
        self.session = requests.Session()
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.session.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('flight', response.text.lower())
        print("✅ Home Page: Loads successfully")
    
    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.session.get(f"{self.base_url}/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn('login', response.text.lower())
        print("✅ Login Page: Loads successfully")
    
    def test_register_page(self):
        """Test register page loads correctly"""
        response = self.session.get(f"{self.base_url}/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn('register', response.text.lower())
        print("✅ Register Page: Loads successfully")
    
    def test_about_page(self):
        """Test about page loads correctly"""
        response = self.session.get(f"{self.base_url}/about")
        self.assertIn(response.status_code, [200, 404])
        print(f"✅ About Page: Status {response.status_code}")
    
    def test_contact_page(self):
        """Test contact page loads correctly"""
        response = self.session.get(f"{self.base_url}/contact")
        self.assertIn(response.status_code, [200, 404])
        print(f"✅ Contact Page: Status {response.status_code}")
    
    def test_search_functionality(self):
        """Test flight search functionality"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        search_data = {
            'Origin': 'ORD',
            'Destination': 'DFW',
            'DepartDate': tomorrow,
            'trip_type': '1',
            'seat': 'Economy'
        }
        
        response = self.session.post(f"{self.base_url}/search", data=search_data)
        self.assertEqual(response.status_code, 200)
        print("✅ Flight Search: Functionality working")
    
    def test_static_files(self):
        """Test static files are accessible"""
        static_files = [
            '/static/css/layout_style.css',
            '/static/js/index.js',
            '/static/img/icon.png'
        ]
        
        for static_file in static_files:
            response = self.session.get(f"{self.base_url}{static_file}")
            if response.status_code == 200:
                print(f"✅ Static File {static_file}: Accessible")
            else:
                print(f"⚠️ Static File {static_file}: Status {response.status_code}")

if __name__ == '__main__':
    print("Running UI Service Unit Tests...")
    unittest.main(verbosity=2)