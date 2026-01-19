from django.core.management.base import BaseCommand
from flight.models import Flight

class Command(BaseCommand):
    help = 'Fix currency mismatch by converting INR flights back to USD'

    def handle(self, *args, **options):
        self.stdout.write('Fixing currency mismatch in American Airlines flights...')
        
        # Exchange rate used in add_aa_flights.py
        inr_to_usd_rate = 82.5
        
        # Find flights with INR prices (typically > 1000)
        problematic_flights = Flight.objects.filter(
            airline='American Airlines',
            economy_fare__gt=1000  # Flights with prices > $1000 are likely in INR
        )
        
        self.stdout.write(f'Found {problematic_flights.count()} flights with INR pricing')
        
        fixed_count = 0
        for flight in problematic_flights:
            # Convert back to USD
            original_economy = flight.economy_fare
            original_business = flight.business_fare
            original_first = flight.first_fare
            
            # Convert INR back to USD
            flight.economy_fare = original_economy / inr_to_usd_rate
            flight.business_fare = original_business / inr_to_usd_rate
            flight.first_fare = original_first / inr_to_usd_rate
            
            flight.save()
            
            self.stdout.write(
                f'Fixed Flight ID {flight.id}: '
                f'Economy INR{original_economy:.0f} -> USD${flight.economy_fare:.2f}, '
                f'Business INR{original_business:.0f} -> USD${flight.business_fare:.2f}, '
                f'First INR{original_first:.0f} -> USD${flight.first_fare:.2f}'
            )
            
            fixed_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully fixed {fixed_count} flights!')
        )