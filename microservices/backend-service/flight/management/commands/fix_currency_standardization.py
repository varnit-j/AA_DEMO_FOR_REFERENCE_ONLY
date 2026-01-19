from django.core.management.base import BaseCommand
from flight.models import Flight, Place, Week
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Standardize all flight prices to INR and add new USD flights properly converted'

    def handle(self, *args, **options):
        self.stdout.write('=== COMPREHENSIVE CURRENCY STANDARDIZATION ===')
        
        # Exchange rate
        USD_TO_INR_RATE = 82.5
        
        # Step 1: Fix existing USD flights by converting to INR
        self.stdout.write('\n1. Converting existing USD flights to INR...')
        usd_flights = Flight.objects.filter(
            airline__icontains='American Airlines',
            economy_fare__lt=500,  # USD flights
            economy_fare__gt=0
        )
        
        self.stdout.write(f'Found {usd_flights.count()} flights with USD pricing')
        
        fixed_usd_count = 0
        for flight in usd_flights:
            original_economy = flight.economy_fare
            original_business = flight.business_fare if flight.business_fare else 0
            original_first = flight.first_fare if flight.first_fare else 0
            
            # Convert USD to INR
            flight.economy_fare = original_economy * USD_TO_INR_RATE
            flight.business_fare = original_business * USD_TO_INR_RATE if original_business > 0 else 0
            flight.first_fare = original_first * USD_TO_INR_RATE if original_first > 0 else 0
            
            flight.save()
            fixed_usd_count += 1
            
            self.stdout.write(
                f'  Fixed Flight {flight.id}: USD${original_economy:.2f} -> INR₹{flight.economy_fare:.0f}'
            )
        
        # Step 2: Remove existing ORD<->DFW flights to replace with new data
        self.stdout.write('\n2. Removing existing ORD<->DFW flights...')
        try:
            ord_place = Place.objects.get(code='ORD')
            dfw_place = Place.objects.get(code='DFW')
            
            existing_ord_dfw = Flight.objects.filter(
                airline__icontains='American Airlines',
                origin__in=[ord_place, dfw_place],
                destination__in=[ord_place, dfw_place]
            )
            
            removed_count = existing_ord_dfw.count()
            existing_ord_dfw.delete()
            self.stdout.write(f'  Removed {removed_count} existing ORD<->DFW flights')
            
        except Place.DoesNotExist:
            self.stdout.write('  ORD or DFW places not found, skipping removal')
        
        # Step 3: Add new ORD<->DFW flights with proper INR conversion
        self.stdout.write('\n3. Adding new ORD<->DFW flights in INR...')
        
        try:
            # Get places and week days
            ord = Place.objects.get(code='ORD')
            dfw = Place.objects.get(code='DFW')
            all_days = Week.objects.all()
            
            # New flight data from user (originally in USD)
            flights_data = [
                # ORD to DFW flights
                {
                    'flight_number': 'AA1838',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(5, 5),
                    'arrival_time': time(7, 40),
                    'usd_price': 150,
                    'plane': 'Boeing 