#!/usr/bin/env python3
"""
Add JFK to LAX American Airlines flights to fix flight search issue
"""
import os
import sys
import django

# Add the backend service to Python path
sys.path.append('microservices/backend-service')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from flight.models import Flight, Place, Week
from datetime import time, timedelta

def add_jfk_lax_flights():
    try:
        # Get places
        jfk = Place.objects.get(code='JFK')
        lax = Place.objects.get(code='LAX')
        print(f"Found JFK: {jfk}")
        print(f"Found LAX: {lax}")
        
        # Get all days
        all_days = Week.objects.all()
        print(f"Found {all_days.count()} days")
        
        # Create JFK to LAX flights
        flights_data = [
            {
                'flight_number': 'AA1001', 
                'depart_time': time(6, 0), 
                'arrival_time': time(9, 30), 
                'plane': 'Boeing 777-300', 
                'economy_fare': 299.0, 
                'business_fare': 899.0, 
                'first_fare': 1499.0
            },
            {
                'flight_number': 'AA1002', 
                'depart_time': time(10, 15), 
                'arrival_time': time(13, 45), 
                'plane': 'Boeing 777-200', 
                'economy_fare': 319.0, 
                'business_fare': 949.0, 
                'first_fare': 1599.0
            },
            {
                'flight_number': 'AA1003', 
                'depart_time': time(14, 30), 
                'arrival_time': time(18, 0), 
                'plane': 'Airbus A321', 
                'economy_fare': 279.0, 
                'business_fare': 849.0, 
                'first_fare': 1399.0
            },
            {
                'flight_number': 'AA1004', 
                'depart_time': time(18, 45), 
                'arrival_time': time(22, 15), 
                'plane': 'Boeing 737-800', 
                'economy_fare': 289.0, 
                'business_fare': 869.0, 
                'first_fare': 1449.0
            }
        ]
        
        created_count = 0
        for flight_data in flights_data:
            # Check if flight already exists
            existing = Flight.objects.filter(
                flight_number=flight_data['flight_number'],
                origin=jfk,
                destination=lax
            ).first()
            
            if existing:
                print(f"Flight {flight_data['flight_number']} already exists, skipping")
                continue
                
            flight = Flight.objects.create(
                origin=jfk,
                destination=lax,
                depart_time=flight_data['depart_time'],
                arrival_time=flight_data['arrival_time'],
                duration=timedelta(hours=5, minutes=30),
                plane=flight_data['plane'],
                airline='American Airlines',
                flight_number=flight_data['flight_number'],
                economy_fare=flight_data['economy_fare'],
                business_fare=flight_data['business_fare'],
                first_fare=flight_data['first_fare']
            )
            flight.depart_day.set(all_days)
            created_count += 1
            print(f"Created flight {flight_data['flight