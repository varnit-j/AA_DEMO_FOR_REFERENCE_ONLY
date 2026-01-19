#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from flight.models import Flight

def check_currency_status():
    print("=== CURRENCY STATUS ANALYSIS ===")
    
    # Get all American Airlines flights
    aa_flights = Flight.objects.filter(airline__icontains='American Airlines')
    print(f"Total American Airlines flights: {aa_flights.count()}")
    
    if aa_flights.count() == 0:
        print("No American Airlines flights found in database")
        return
    
    print("\n=== FLIGHT PRICE ANALYSIS (Sample of 10 flights) ===")
    for flight in aa_flights[:10]:
        print(f"Flight ID {flight.id}: {flight.origin.code}->{flight.destination.code}")
        print(f"  Economy: {flight.economy_fare}")
        print(f"  Business: {flight.business_fare}")
        print(f"  First: {flight.first_fare}")
        
        # Analyze if prices are in USD or INR
        if flight.economy_fare:
            if flight.economy_fare < 500:
                print(f"  -> Likely USD (${flight.economy_fare})")
            else:
                print(f"  -> Likely INR (Rs.{flight.economy_fare})")
        print()
    
    # Check for inconsistencies
    print("=== CURRENCY INCONSISTENCY ANALYSIS ===")
    usd_flights = aa_flights.filter(economy_fare__lt=500, economy_fare__gt=0)
    inr_flights = aa_flights.filter(economy_fare__gte=500)
    
    print(f"Flights with USD pricing (< $500): {usd_flights.count()}")
    print(f"Flights with INR pricing (>= Rs.500): {inr_flights.count()}")
    
    if usd_flights.count() > 0 and inr_flights.count() > 0:
        print("WARNING: CURRENCY MISMATCH DETECTED!")
        print("Some flights are in USD, others in INR")
        print("\nSample USD flights:")
        for flight in usd_flights[:3]:
            print(f"  Flight {flight.id}: {flight.origin.code}->{flight.destination.code} Economy: ${flight.economy_fare}")
        print("\nSample INR flights:")
        for flight in inr_flights[:3]:
            print(f"  Flight {flight.id}: {flight.origin.code}->{flight.destination.code} Economy: Rs.{flight.economy_fare}")
    elif usd_flights.count() > 0:
        print("All flights appear to be in USD")
    elif inr_flights.count() > 0:
        print("All flights appear to be in INR")
    
    # Check for the new USD flights that were added
    print("\n=== CHECKING FOR NEW USD FLIGHTS ===")
    new_usd_flights = aa_flights.filter(
        economy_fare__gte=150, 
        economy_fare__lte=250,
        origin__code__in=['ORD', 'DFW'],
        destination__code__in=['ORD', 'DFW']
    )
    print(f"Potential new USD flights (ORD<->DFW, $150-250): {new_usd_flights.count()}")
    for flight in new_usd_flights[:5]:
        print(f"  Flight {flight.id}: {flight.origin.code}->{flight.destination.code} Economy: ${flight.economy_fare}")

if __name__ == "__main__":
    check_currency_status()