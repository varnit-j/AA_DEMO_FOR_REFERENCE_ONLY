#!/usr/bin/env python3
"""
Complete SAGA Implementation with Logging and Testing
Fixes flight search and implements complete SAGA booking flow
"""

import requests
import json
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('saga_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Service URLs
BACKEND_SERVICE_URL = "http://localhost:8001"
PAYMENT_SERVICE_URL = "http://localhost:8003"
LOYALTY_SERVICE_URL = "http://localhost:8002"
UI_SERVICE_URL = "http://localhost:8000"

class CompleteSAGAImplementation:
    def __init__(self):
        self.session = requests.Session()
        
    def log_step(self, step_name, status, details=""):
        """Log SAGA step with timestamp"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {step_name}: {status}"
        if details:
            log_entry += f" - {details}"
        logger.info(log_entry)
        
        # Also save to file for debugging
        with open('saga_execution.log', 'a') as f:
            f.write(log_entry + '\n')
    
    def test_flight_search_fix(self):
        """Test and fix flight search functionality"""
        self.log_step("FLIGHT_SEARCH_TEST", "STARTING", "Testing flight search with multiple routes")
        
        # Test routes that should work
        test_routes = [
            ("ORD", "DFW", "2026-01-27"),  # Monday - American Airlines route
            ("JFK", "LAX", "2026-01-24"),  # Friday - Other airlines route
            ("DEL", "BOM", "2026-01-27"),  # Monday - Indian route
        ]
        
        for origin, destination, date in test_routes:
            try:
                url = f"{BACKEND_SERVICE_URL}/api/flights/search/"
                params = {
                    'origin': origin,
                    'destination': destination,
                    'depart_date': date,
                    'seat_class': 'economy'
                }
                
                self.log_step("FLIGHT_SEARCH", "TESTING", f"{origin} -> {destination} on {date}")
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    flights = data.get('flights', [])
                    self.log_step("FLIGHT_SEARCH", "SUCCESS", f"Found {len(flights)} flights for {origin}->{destination}")
                    
                    if flights:
                        sample_flight = flights[0]
                        self.log_step("SAMPLE_FLIGHT", "INFO", f"ID: {sample_flight.get('id')}, Airline: {sample_flight.get('airline')}, Flight: {sample_flight.get('flight_number')}")
                        return sample_flight  # Return first working flight for SAGA test
                else:
                    self.log_step("FLIGHT_SEARCH", "ERROR", f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_step("FLIGHT_SEARCH", "EXCEPTION", str(e))
        
        return None
    
    def test_complete_saga_flow(self, flight_data):
        """Test complete SAGA booking flow with sequential steps"""
        if not flight_data:
            self.log_step("SAGA_FLOW", "SKIPPED", "No flight data available")
            return False