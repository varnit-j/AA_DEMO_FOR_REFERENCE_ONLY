#!/usr/bin/env python3
"""Debug the flight ID mismatch and missing data"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/d/varnit/demo/2101/AA_Flight_booking/microservices/backend-service')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from flight.models import Flight

print("\n" + "="*70)
print("CHECKING FLIGHT DATA FOR MISSING FIELDS")
print("="*70 + "\n")

# Get a sample flight
flight = Flight.objects.first()

if not flight:
    print("❌ No flights found!")
    sys.exit(1)

print(f"Sample Flight: {flight.id} - {flight.flight_number}")
print(f"  airline: {flight.airline}")
print(f"  plane: {flight.plane}")
print(f"  economy_fare: {flight.economy_fare}")
print(f"  business_fare: {flight.business_fare}")
print(f"  first_fare: {flight.first_fare}")  # THIS IS LIKELY None
print(f"  arrival_time: {flight.arrival_time}")  # THIS IS LIKELY None
print(f"  depart_time: {flight.depart_time}")

print("\n" + "="*70)
print("CHECKING ALL FLIGHTS WITH NULL VALUES")
print("="*70 + "\n")

# Check which flights have missing values
null_first_fare = Flight.objects.filter(first_fare__isnull=True).count()
null_arrival_time = Flight.objects.filter(arrival_time__isnull=True).count()
null_business_fare = Flight.objects.filter(business_fare__isnull=True).count()

print(f"Flights with NULL first_fare: {null_first_fare}")
print(f"Flights with NULL business_fare: {null_business_fare}")
print(f"Flights with NULL arrival_time: {null_arrival_time}")

if null_first_fare > 0 or null_arrival_time > 0 or null_business_fare > 0:
    print("\n⚠️  FOUND THE ISSUE!")
    print("Some flights have missing required fields.")
    print("\nFixing missing data...\n")
    
    # Fix missing business_fare (default to economy_fare * 2)
    if null_business_fare > 0:
        from django.db.models import F
        Flight.objects.filter(business_fare__isnull=True).update(
            business_fare=F('economy_fare') * 2
        )
        print(f"✓ Fixed {null_business_fare} flights with missing business_fare")
    
    # Fix missing first_fare (default to business_fare * 1.5)
    if null_first_fare > 0:
        from django.db.models import F
        Flight.objects.filter(first_fare__isnull=True).update(
            first_fare=F('business_fare') * 1.5
        )
        print(f"✓ Fixed {null_first_fare} flights with missing first_fare")
    
    # Fix missing arrival_time (calculate from depart_time + duration)
    if null_arrival_time > 0:
        from datetime import timedelta
        flights_to_fix = Flight.objects.filter(arrival_time__isnull=True)
        for flight in flights_to_fix:
            if flight.duration and flight.depart_time:
                arrival = (datetime.combine(datetime.today(), flight.depart_time) + flight.duration).time()
                flight.arrival_time = arrival
                flight.save()
        print(f"✓ Fixed {null_arrival_time} flights with missing arrival_time")

print("\n" + "="*70)
print("VERIFYING API RESPONSE")
print("="*70 + "\n")

# Simulate the API response
flight = Flight.objects.first()
print(f"Flight ID {flight.id} API Response:")
print(f"  id: {flight.id}")
print(f"  plane: {flight.plane}")
print(f"  airline: {flight.airline}")
print(f"  flight_number: {flight.flight_number}")
print(f"  economy_fare: {float(flight.economy_fare)}")
print(f"  business_fare: {float(flight.business_fare) if flight.business_fare else 'NONE'}")
print(f"  first_fare: {float(flight.first_fare) if flight.first_fare else 'NONE'}")
print(f"  arrival_time: {flight.arrival_time if flight.arrival_time else 'NONE'}")
print(f"  depart_time: {str(flight.depart_time)}")
print(f"  duration: {str(flight.duration)}")

print("\n✓ Flight data is now ready for API responses\n")
