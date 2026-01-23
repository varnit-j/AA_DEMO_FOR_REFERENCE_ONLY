
#!/usr/bin/env python3
"""
Comprehensive SAGA Flow Test and Debug Script
Tests the complete end-to-end SAGA functionality and diagnoses issues
"""

import requests
import json
import time
import sys
from datetime import datetime

# Service URLs
UI_SERVICE_URL = "http://localhost:8000"
BACKEND_SERVICE_URL = "http://localhost:8001"
PAYMENT_SERVICE_URL = "http://localhost:8003"
LOYALTY_SERVICE_URL = "http://localhost:8002"

class SAGAFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_service_connectivity(self):
        """Test if all microservices are running"""
        print("\n🔍 Testing Service Connectivity...")
        
        services = [
            ("UI Service", UI_SERVICE_URL),
            ("Backend Service", BACKEND_SERVICE_URL),
            ("Payment Service", PAYMENT_SERVICE_URL),
            ("Loyalty Service", LOYALTY_SERVICE_URL)
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(f"{url}/", timeout=5)
                if response.status_code in [200, 404]:  # 404 is OK for root path
                    self.log_test(f"{service_name} Connectivity", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"{service_name} Connectivity", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{service_name} Connectivity", "FAIL", str(e))
    
    def test_flight_data_availability(self):
        """Test if flight data is available in backend service"""
        print("\n🛫 Testing Flight Data Availability...")
        
        try:
            # Test flight search endpoint
            search_params = {
                'origin': 'New York',
                'destination': 'Los Angeles',
                'trip_type': '1',
                'depart_date': '2026-01-25',
                'seat_class': 'economy'
            }
            
            response = requests.get(f"{BACKEND_SERVICE_URL}/api/flights/search/", params=search_params, timeout=10)
            
            if response.status_code == 200:
                flight_data = response.json()
                flights = flight_data.get('flights', [])
                
                if flights:
                    self.log_test("Flight Data Search", "PASS", f"Found {len(flights)} flights")
                    
                    # Test individual flight retrieval
                    first_flight = flights[0]
                    flight_id = first_flight.get('id')
                    
                    if flight_id:
                        flight_response = requests.get(f"{BACKEND_SERVICE_URL}/api/flights/{flight_id}/", timeout=5)
                        if flight_response.status_code == 200:
                            flight_detail = flight_response.json()
                            self.log_test("Individual Flight Retrieval", "PASS", f"Flight {flight_id} retrieved successfully")