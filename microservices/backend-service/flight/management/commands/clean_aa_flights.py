from django.core.management.base import BaseCommand
from flight.models import Flight, Place, Week
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Clean recreate AA flights: Remove all AA flights and add new ones from USD data converted to INR'

    def handle(self, *args, **options):
        self.stdout.write('=== CLEAN AA FLIGHTS RECREATION ===')
        
        USD_TO_INR = 82.5
        
        # Step 1: Remove all AA flights
        self.stdout.write('\n1. Removing all American Airlines flights...')
        aa_flights = Flight.objects.filter(airline__icontains='American Airlines')
        count = aa_flights.count()
        aa_flights.delete()
        self.stdout.write(f'   Removed {count} flights')
        
        # Step 2: Add new flights
        self.stdout.write('\n2. Adding new flights from USD data...')
        
        try:
            ord = Place.objects.get(code='ORD')
            dfw = Place.objects.get(code='DFW')
            all_days = Week.objects.all()
            
            # User's flight data (USD prices)
            flights = [
                # ORD->DFW
                {'num': 'AA1838', 'orig': ord, 'dest': dfw, 'dept': time(5,5), 'arr': time(7,40), 'usd': 150},
                {'num': 'AA2113', 'orig': ord, 'dest': dfw, 'dept': time(6,54), 'arr': time(9,29), 'usd': 160},
                {'num': 'AA2156', 'orig': ord, 'dest': dfw, 'dept': time(8,10), 'arr': time(10,45), 'usd': 170},
                {'num': 'AA1213', 'orig': ord, 'dest': dfw, 'dept': time(10,19), 'arr': time(12,54), 'usd': 180},
                {'num': 'AA1362', 'orig': ord, 'dest': dfw, 'dept': time(15,23), 'arr': time(17,58), 'usd': 200},
                {'num': 'AA2544', 'orig': ord, 'dest': dfw, 'dept': time(18,55), 'arr': time(21,30), 'usd': 220},
                # DFW->ORD
                {'num': 'AA328', 'orig': dfw, 'dest': ord, 'dept': time(8,9), 'arr': time(10,42), 'usd': 150},
                {'num': 'AA328B', 'orig': dfw, 'dest': ord, 'dept': time(13,0), 'arr': time(15,33), 'usd': 170},
                {'num': 'AA328C', 'orig': dfw, 'dest': ord, 'dept': time(20,0), 'arr': time(22,33), 'usd': 200},
            ]
            
            created = 0
            for f in flights:
                # Convert USD to INR
                inr_price = f['usd'] * USD_TO_INR
                
                # Calculate duration
                dept_td = timedelta(hours=f['dept'].hour, minutes=f['dept'].minute)
                arr_td = timedelta(hours=f['arr'].hour, minutes=f['arr'].minute)
                if arr_td < dept_td:
                    arr_td += timedelta(days=1)
                duration = arr_td - dept_td
                
                # Create flight
                flight = Flight.objects.create(
                    origin=f['orig'],
                    destination=f['dest'],
                    depart_time=f['dept'],
                    arrival_time=f['arr'],
                    duration=duration,
                    plane='Boeing 737-800',
                    airline='American Airlines',
                    economy_fare=inr_price,
                    business_fare=inr_price * 2.5,
                    first_fare=inr_price * 4.0
                )
                
                flight.depart_day.set(all_days)
                created += 1
                
                self.stdout.write(
                    f'   {f["num"]}: {f["orig"].code}->{f["dest"].code} '
                    f'USD${f["usd"]} -> INR Rs.{inr_price:.0f}'
                )
            
            self.stdout.write(f'\nSUCCESS: Created {created} flights')
            
        except Exception as e:
            self.stdout.write(f'ERROR: {e}')
        
        # Step 3: Verify
        self.stdout.write('\n3. Verification...')
        aa_flights = Flight.objects.filter(airline__icontains='American Airlines')
        self.stdout.write(f'   Total AA flights: {aa_flights.count()}')
        
        inr_flights = aa_flights.filter(economy_fare__gte=1000)
        usd_flights = aa_flights.filter(economy_fare__lt=1000, economy_fare__gt=0)
        
        self.stdout.write(f'   INR flights (>=Rs.1000): {inr_flights.count()}')
        self.stdout.write(f'   USD flights (<$1000): {usd_flights.count()}')
        
        if usd_flights.count() == 0:
            self.stdout.write('SUCCESS: All flights in INR!')
        else:
            self.stdout.write('WARNING: Some USD flights remain')
        
        self.stdout.write('\n=== CLEAN RECREATION COMPLETE ===')