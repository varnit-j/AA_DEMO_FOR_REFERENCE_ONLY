from django.core.management.base import BaseCommand
from flight.models import Flight, Place, Week
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Fix currency issues: Convert all flights to INR and add new ORD-DFW flights'

    def handle(self, *args, **options):
        self.stdout.write('=== FINAL CURRENCY FIX ===')
        
        USD_TO_INR_RATE = 82.5
        
        # Step 1: Convert any remaining USD flights to INR
        self.stdout.write('\n1. Converting USD flights to INR...')
        usd_flights = Flight.objects.filter(
            airline__icontains='American Airlines',
            economy_fare__lt=500,
            economy_fare__gt=0
        )
        
        for flight in usd_flights:
            flight.economy_fare = flight.economy_fare * USD_TO_INR_RATE
            if flight.business_fare:
                flight.business_fare = flight.business_fare * USD_TO_INR_RATE
            if flight.first_fare:
                flight.first_fare = flight.first_fare * USD_TO_INR_RATE
            flight.save()
            self.stdout.write(f'  Converted Flight {flight.id}')
        
        # Step 2: Remove existing ORD<->DFW flights
        self.stdout.write('\n2. Removing old ORD<->DFW flights...')
        try:
            ord = Place.objects.get(code='ORD')
            dfw = Place.objects.get(code='DFW')
            
            old_flights = Flight.objects.filter(
                airline__icontains='American Airlines',
                origin__in=[ord, dfw],
                destination__in=[ord, dfw]
            )
            count = old_flights.count()
            old_flights.delete()
            self.stdout.write(f'  Removed {count} old flights')
        except:
            self.stdout.write('  Could not remove old flights')
        
        # Step 3: Add new flights with correct INR prices
        self.stdout.write('\n3. Adding new ORD<->DFW flights...')
        try:
            ord = Place.objects.get(code='ORD')
            dfw = Place.objects.get(code='DFW')
            all_days = Week.objects.all()
            
            # User's new flight data (convert USD to INR)
            new_flights = [
                # ORD to DFW
                {'origin': ord, 'dest': dfw, 'dept': time(5,5), 'arr': time(7,40), 'usd': 150},
                {'origin': ord, 'dest': dfw, 'dept': time(6,54), 'arr': time(9,29), 'usd': 160},
                {'origin': ord, 'dest': dfw, 'dept': time(8,10), 'arr': time(10,45), 'usd': 170},
                {'origin': ord, 'dest': dfw, 'dept': time(10,19), 'arr': time(12,54), 'usd': 180},
                {'origin': ord, 'dest': dfw, 'dept': time(15,23), 'arr': time(17,58), 'usd': 200},
                {'origin': ord, 'dest': dfw, 'dept': time(18,55), 'arr': time(21,30), 'usd': 220},
                # DFW to ORD
                {'origin': dfw, 'dest': ord, 'dept': time(8,9), 'arr': time(10,42), 'usd': 150},
                {'origin': dfw, 'dest': ord, 'dept': time(13,0), 'arr': time(15,33), 'usd': 170},
                {'origin': dfw, 'dest': ord, 'dept': time(20,0), 'arr': time(22,33), 'usd': 200},
            ]
            
            created_count = 0
            for flight_data in new_flights:
                # Convert USD to INR
                inr_price = flight_data['usd'] * USD_TO_INR_RATE
                
                # Calculate duration
                dept_td = timedelta(hours=flight_data['dept'].hour, minutes=flight_data['dept'].minute)
                arr_td = timedelta(hours=flight_data['arr'].hour, minutes=flight_data['arr'].minute)
                if arr_td < dept_td:
                    arr_td += timedelta(days=1)
                duration = arr_td - dept_td
                
                # Create flight
                flight = Flight.objects.create(
                    origin=flight_data['origin'],
                    destination=flight_data['dest'],
                    depart_time=flight_data['dept'],
                    arrival_time=flight_data['arr'],
                    duration=duration,
                    plane='Boeing 737-800',
                    airline='American Airlines',
                    economy_fare=inr_price,
                    business_fare=inr_price * 2.5,
                    first_fare=inr_price * 4.0
                )
                
                flight.depart_day.set(all_days)
                created_count += 1
                
                self.stdout.write(
                    f'  Created: {flight_data["origin"].code}->{flight_data["dest"].code} '
                    f'USD${flight_data["usd"]} -> INR₹{inr_price:.0f}'
                )
            
            self.stdout.write(f'\n✅ Successfully created {created_count} new flights')
            
        except Exception as e:
            self.stdout.write(f'❌ Error adding new flights: {e}')
        
        # Step 4: Verify final state
        self.stdout.write('\n4. Final verification...')
        aa_flights = Flight.objects.filter(airline__icontains='American Airlines')
        usd_count = aa_flights.filter(economy_fare__lt=500, economy_fare__gt=0).count()
        inr_count = aa_flights.filter(economy_fare__gte=500).count()
        
        self.stdout.write(f'  Total AA flights: {aa_flights.count()}')
        self.stdout.write(f'  USD flights remaining: {usd_count}')
        self.stdout.write(f'  INR flights: {inr_count}')
        
        if usd_count == 0:
            self.stdout.write('✅ SUCCESS: All flights now in INR!')
        else:
            self.stdout.write('⚠️  WARNING: Some USD flights still remain')
        
        self.stdout.write('\n=== CURRENCY FIX COMPLETE ===')