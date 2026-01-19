from django.core.management.base import BaseCommand
from flight.models import Flight, Place, Week
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Clean recreate of American Airlines flights from source USD data converted to INR'

    def handle(self, *args, **options):
        self.stdout.write('=== CLEAN RECREATION OF AA FLIGHTS ===')
        
        # Exchange rate: USD to INR
        USD_TO_INR_RATE = 82.5
        
        # Step 1: Remove ALL existing American Airlines flights
        self.stdout.write('\n1. Removing all existing American Airlines flights...')
        existing_aa_flights = Flight.objects.filter(airline__icontains='American Airlines')
        removed_count = existing_aa_flights.count()
        existing_aa_flights.delete()
        self.stdout.write(f'   Removed {removed_count} existing AA flights')
        
        # Step 2: Add new flights from source USD data, converted to INR
        self.stdout.write('\n2. Adding new flights from source data (USD -> INR)...')
        
        try:
            # Get required places
            ord = Place.objects.get(code='ORD')
            dfw = Place.objects.get(code='DFW')
            all_days = Week.objects.all()
            
            # Source flight data from user (in USD, convert to INR)
            source_flights = [
                # ORD to DFW flights
                {'flight_number': 'AA1838', 'origin': ord, 'destination': dfw, 'depart_time': time(5, 5), 'arrival_time': time(7, 40), 'usd_price': 150},
                {'flight_number': 'AA2113', 'origin': ord, 'destination': dfw, 'depart_time': time(6, 54), 'arrival_time': time(9, 29), 'usd_price': 160},
                {'flight_number': 'AA2156', 'origin': ord, 'destination': dfw, 'depart_time': time(8, 10), 'arrival_time': time(10, 45), 'usd_price': 170},
                {'flight_number': 'AA1213', 'origin': ord, 'destination': dfw, 'depart_time': time(10, 19), 'arrival_time': time(12, 54), 'usd_price': 180},
                {'flight_number': 'AA1362', 'origin': ord, 'destination': dfw, 'depart_time': time(15, 23), 'arrival_time': time(17, 58), 'usd_price': 200},
                {'flight_number': 'AA2544', 'origin': ord, 'destination': dfw, 'depart_time': time(18, 55), 'arrival_time': time(21, 30), 'usd_price': 220},
                # DFW to ORD flights
                {'flight_number': 'AA328', 'origin': dfw, 'destination': ord, 'depart_time': time(8, 9), 'arrival_time': time(10, 42), 'usd_price': 150},
                {'flight_number': 'AA328B', 'origin': dfw, 'destination': ord, 'depart_time': time(13, 0), 'arrival_time': time(15, 33), 'usd_price': 170},
                {'flight_number': 'AA328C', 'origin': dfw, 'destination': ord, 'depart_time': time(20, 0), 'arrival_time': time(22, 33), 'usd_price':