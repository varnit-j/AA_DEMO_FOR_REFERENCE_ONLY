#!/usr/bin/env python3
"""Check what flights exist in backend database"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/d/varnit/demo/2101/AA_Flight_booking/microservices/backend-service')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from flight.models import Flight

print(f"\nFlights in backend database:")
flights = Flight.objects.all()
print(f"Total: {flights.count()}\n")

if flights.count() == 0:
    print("❌ NO FLIGHTS FOUND - Database is empty!")
    print("\nCreating sample flights...")
    
    from flight.models import Place, Week
    from datetime import time
    
    # Create places
    delhi, _ = Place.objects.get_or_create(name='Delhi', code='DEL')
    mumbai, _ = Place.objects.get_or_create(name='Mumbai', code='BOM')
    bangalore, _ = Place.objects.get_or_create(name='Bangalore', code='BLR')
    
    # Create weeks
    monday, _ = Week.objects.get_or_create(number=0, name='Monday')
    wed, _ = Week.objects.get_or_create(number=2, name='Wednesday')
    fri, _ = Week.objects.get_or_create(number=4, name='Friday')
    
    # Create flight 1
    f1 = Flight.objects.create(
        flight_number='AI101',
        airline='Air India',
        origin=delhi,
        destination=mumbai,
        depart_time=time(8, 0),
        duration=120,
        economy_fare=5000.0,
        business_fare=12000.0
    )
    f1.depart_day.set([monday, wed, fri])
    print(f"✓ Created Flight 1: {f1.flight_number}")
    
    # Create flight 2
    f2 = Flight.objects.create(
        flight_number='AI202',
        airline='Air India',
        origin=mumbai,
        destination=bangalore,
        depart_time=time(14, 30),
        duration=90,
        economy_fare=3500.0,
        business_fare=8500.0
    )
    f2.depart_day.set([monday, wed, fri])
    print(f"✓ Created Flight 2: {f2.flight_number}")
else:
    for i, f in enumerate(flights[:10], 1):
        print(f"{i}. ID={f.id} | {f.flight_number} ({f.airline})")
        print(f"   {f.origin} → {f.destination} | Fare: ₹{f.economy_fare}")

print(f"\n✓ Flight data ready for testing\n")
