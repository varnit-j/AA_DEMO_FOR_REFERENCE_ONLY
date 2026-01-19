#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from flight.models import Flight

def check_flight_times():
    print("=== FLIGHT TIMES CHECK ===")
    
    flights = Flight.objects.filter(airline__icontains='American Airlines')
    print(f"Total AA flights: {flights.count()}")
    
    for flight in flights:
        print(f"Flight {flight.id}: {flight.origin.code}->{flight.destination.code}")
        print(f"  Depart: {flight.depart_time}")
        print(f"  Arrive: {flight.arrival_time}")
        print(f"  Duration: {flight.duration}")
        print(f"  Economy: Rs.{flight.economy_fare}")
        print()

if __name__ == "__main__":
    check_flight_times()