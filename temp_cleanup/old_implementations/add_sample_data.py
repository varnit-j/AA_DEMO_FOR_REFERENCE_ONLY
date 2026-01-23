#!/usr/bin/env python3
"""
Add sample flight data for testing
"""
import os
import sys
import django

# Add the backend service to Python path
sys.path.append('AA_Flight_booking/microservices/backend-service')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from flight.models import Place, Flight

def add_sample_data():
    """Add sample cities and flights"""
    
    # Add major US cities
    cities = [
        ('Dallas', 'Dallas/Fort Worth International Airport', 'DFW'),
        ('Chicago', 'Chicago O\'Hare International Airport', 'ORD'),
        ('New York', 'John F. Kennedy International Airport', 'JFK'),
        ('Los Angeles', 'Los Angeles International Airport', 'LAX'),
        ('Miami', 'Miami International Airport', 'MIA'),
        ('Boston', 'Logan International Airport', 'BOS'),
        ('Atlanta', 'Hartsfield-Jackson Atlanta International Airport', 'ATL'),
        ('Denver', 'Denver International Airport', 'DEN'),
        ('Seattle', 'Seattle-Tacoma International Airport', 'SEA'),
        ('Phoenix', 'Phoenix Sky Harbor International Airport', 'PHX')
    ]
    
    print("Adding cities...")
    city_objects = {}
    for city, airport, code in cities:
        place, created = Place.objects.get_or_create(
            city=city,
            defaults={'airport': airport, 'code': code, 'country': 'US'}
        )
        city_objects[city] = place
        print(f"{'Created' if created else 'Found'}: {city}")
    
    # Add sample flights
    print("\nAdding sample flights...")
    sample_flights = [
        # Dallas to Chicago
        {
            'origin': 'Dallas', 'destination': 'Chicago',
            'flight_number': 'AA1001', 'airline': 'American Airlines',
            'plane': 'Boeing 737', 'depart_time': '08:00:00', 'arrival_time': '10:30:00',
            'duration': '2:30', 'economy_fare': 299.99, 'business_fare': 599.99, 'first_fare': 999.99
        },
        # Chicago to Dallas
        {
            'origin': 'Chicago', 'destination': 'Dallas',
            'flight_number': 'AA1002', 'airline': 'American Airlines',
            'plane': 'Boeing 737', 'depart_time': '14:00:00', 'arrival_time': '16:30:00',
            'duration': '2:30', 'economy_fare': 299.99, 'business_fare': 599.99, 'first_fare': 999.99
        },
        # New York to Los Angeles
        {
            'origin': 'New York', 'destination': 'Los Angeles',
            'flight_number': 'AA2001', 'airline': 'American Airlines',
            'plane': 'Boeing 777', 'depart_time': '09:00:00', 'arrival_time': '12:00:00',
            'duration': '6:00', 'economy_fare': 399.99, 'business_fare': 799.99, 'first_fare': 1299.99
        },
        # Los Angeles to New York
        {
            'origin': 'Los Angeles', 'destination': 'New York',
            'flight_number': 'AA2002', 'airline': 'American Airlines',
            'plane': 'Boeing 777', 'depart_time': '15:00:00', 'arrival_time': '23:00:00',
            'duration': '5:00', 'economy_fare': 399.99, 'business_fare': 799.99, 'first_fare': 1299.99
        },
        # Miami to Boston
        {
            'origin': 'Miami', 'destination': 'Boston',
            'flight_number': 'AA3001', 'airline': 'American Airlines',
            'plane': 'Airbus A320', 'depart_time': '11:00:00', 'arrival_time': '14:30:00',
            'duration': '3:30', 'economy_fare': 249.99, 'business_fare': 499.99, 'first_fare': 799.99
        },
        # Boston to Miami
        {
            'origin': 'Boston', 'destination': 'Miami',
            'flight_number': 'AA3002', 'airline': 'American Airlines',
            'plane': 'Airbus A320', 'depart_time': '16:00:00', 'arrival_time': '19:30:00',
            'duration': '3:30', 'economy_fare': 249.99, 'business_fare': 499.99, 'first_fare': 799.99
        }
    ]
    
    flight_count = 0
    for flight_data in sample_flights:
        origin_place = city_objects[flight_data['origin']]
        destination_place = city_objects[flight_data['destination']]
        
        flight, created = Flight.objects.get_or_create(
            origin=origin_place,
            destination=destination_place,
            depart_time=flight_data['depart_time'],
            defaults={
                'airline': flight_data['airline'],
                'plane': flight_data['plane'],
                'arrival_time': flight_data['arrival_time'],
                'duration': flight_data['duration'],
                'economy_fare': flight_data['economy_fare'],
                'business_fare': flight_data['business_fare'],
                'first_fare': flight_data['first_fare']
            }
        )
        if created:
            flight_count += 1
            print(f"Created flight: {flight_data['flight_number']} ({flight_data['origin']} -> {flight_data['destination']})")
        else:
            print(f"Flight exists: {flight_data['flight_number']}")
    
    print(f"\nSample data setup complete!")
    print(f"Cities: {len(cities)}")
    print(f"New flights added: {flight_count}")
    print(f"Total flights in database: {Flight.objects.count()}")

if __name__ == "__main__":
    add_sample_data()