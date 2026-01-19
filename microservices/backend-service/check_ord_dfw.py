#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from flight.models import Flight, Place

def check_ord_dfw():
    try:
        ord_place = Place.objects.get(code='ORD')
        dfw_place = Place.objects.get(code='DFW')
        print(f"Found places: {ord_place} and {dfw_place}")
        
        ord_dfw_flights = Flight.objects.filter(origin=ord_place, destination=dfw_place, airline__icontains='American')
        dfw_ord_flights = Flight.objects.filter(origin=dfw_place, destination=ord_place, airline__icontains='American')
        
        print(f'ORD->DFW flights: {ord_dfw_flights.count()}')
        print(f'DFW->ORD flights: {dfw_ord_flights.count()}')
        
        if ord_dfw_flights.count() > 0:
            print("\nORD->DFW flights:")
            for flight in ord_dfw_flights[:5]:
                print(f'  Flight {flight.id}: Economy={flight.economy_fare}, Business={flight.business_fare}, First={flight.first_fare}')
        
        if dfw_ord_flights.count() > 0:
            print("\nDFW->ORD flights:")
            for flight in dfw_ord_flights[:5]:
                print(f'  Flight {flight.id}: Economy={flight.economy_fare}, Business={flight.business_fare}, First={flight.first_fare}')
                
    except Place.DoesNotExist as e:
        print(f'Place not found: {e}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    check_ord_dfw()