#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from flight.models import Flight

def test_flight_numbers():
    print("=== FLIGHT NUMBER VALIDATION TEST ===")
    
    flights = Flight.objects.filter(airline__icontains='American Airlines')
    print(f"Found {flights.count()} American Airlines flights")
    
    print("\nFlight Details:")
    for flight in flights:
        print(f"ID: {flight.id}")
        print(f"  Flight Number: '{flight.flight_number}'")
        print(f"  Aircraft Type: '{flight.plane}'")
        print(f"  Airline: '{flight.airline}'")
        print(f"  Route: {flight.origin.code} -> {flight.destination.code}")
        print(f"  Time: {flight.depart_time} -> {flight.arrival_time}")
        print(f"  Economy Fare: ${flight.economy_fare}")
        print("---")
    
    # Check for missing flight numbers
    missing_flight_numbers = flights.filter(flight_number__isnull=True)
    empty_flight_numbers = flights.filter(flight_number='')
    
    print(f"\nValidation Results:")
    print(f"  Flights with NULL flight_number: {missing_flight_numbers.count()}")
    print(f"  Flights with empty flight_number: {empty_flight_numbers.count()}")
    
    if missing_flight_numbers.count() > 0 or empty_flight_numbers.count() > 0:
        print("  ❌ ISSUE: Some flights are missing flight numbers!")
    else:
        print("  ✅ SUCCESS: All flights have flight numbers!")

if __name__ == '__main__':
    test_flight_numbers()