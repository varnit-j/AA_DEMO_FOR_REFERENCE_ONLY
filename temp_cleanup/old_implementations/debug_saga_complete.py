#!/usr/bin/env python3
"""
Complete SAGA Debug Script - Identifies and fixes flight search and SAGA issues
"""

import requests
import json
import sys
import os
from datetime import datetime

# Service URLs
UI_SERVICE_URL = "http://localhost:8000"
BACKEND_SERVICE_URL = "http://localhost:8001"
PAYMENT_SERVICE_URL = "http://localhost:8003"
LOYALTY_SERVICE_URL = "http://localhost:8002"

class SAGADebugger:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, issue_type, description, severity="HIGH"):
        issue = {
            'type': issue_type,
            'description': description,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.issues_found.append(issue)
        print(f"🔍 [{severity}] {issue_type}: {description}")
    
    def log_fix(self, fix_description):
        fix = {
            'description': fix_description,
            'timestamp': datetime.now().isoformat()
        }
        self.fixes_applied.append(fix)
        print(f"✅ FIX APPLIED: {fix_description}")
    
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
                    print(f"✅ {service_name}: RUNNING (Status: {response.status_code})")
                else:
                    self.log_issue("SERVICE_DOWN", f"{service_name} returned status {response.status_code}")
            except Exception as e:
                self.log_issue("SERVICE_DOWN", f"{service_name} not accessible: {str(e)}")
    
    def test_flight_search_api(self):
        """Test flight search API directly"""
        print("\n🔍 Testing Flight Search API...")
        
        # Test parameters that should work
        test_params = {
            'origin': 'NYC',
            'destination': 'LAX', 
            'depart_date': '2026-01-25',
            'seat_class': 'economy'
        }
        
        try:
            response = requests.get(f"{BACKEND_SERVICE_URL}/api/flights/search/", 
                                  params=test_params, timeout=10)
            
            print(f"Flight Search API Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    flights = data.get('flights', [])
                    print(f"✅ Flight Search API: WORKING - Found {len(flights)} flights")
                    
                    if len(flights) == 0:
                        self.log_issue("NO_FLIGHTS", "Flight search returns empty results")
                        print("🔍 Checking database content...")
                        self._check_database_content()
                    else:
                        print(f"Sample flight: {flights[0] if flights else 'None'}")
                        
                except json.JSONDecodeError as e:
                    self.log_issue("API_ERROR", f"Flight search API returned invalid JSON: {str