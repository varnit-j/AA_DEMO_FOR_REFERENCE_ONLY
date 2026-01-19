from django.core.management.base import BaseCommand
from flight.models import Flight

class Command(BaseCommand):
    help = 'Fix currency by converting USD flights back to INR to match database standard'

    def handle(self, *args, **options):
        self.stdout.write('Fixing currency: Converting USD flights back to INR...')
        
        # Exchange rate
        usd_to_inr_rate = 82.5
        
        # Find flights that were incorrectly converted to very small USD values
        # These are the flights that were originally USD but got divided by 82.5
        problematic_flights = Flight.objects.filter(
            airline='American Airlines',
            economy_fare__lt=300  # Flights with prices < $300 are likely incorrectly converted
        )
        
        self.stdout.write(f'Found {problematic_flights.count()} flights with USD pricing that need INR conversion')
        
        fixed_count = 0
        for flight in problematic_flights:
            # These were originally USD values that got incorrectly divided
            # We need to multiply back by 82.5 to get the original USD, then multiply again to get INR
            original_usd_economy = flight.economy_fare * usd_to_inr_rate  # Get back original USD
            original_usd_business = flight.business_fare * usd_to_inr_rate if flight.business_fare > 0 else 0
            original_usd_first = flight.first_fare * usd_to_inr_rate if flight.first_fare > 0 else 0
            
            # Now convert USD to INR for database storage
            flight.economy_fare = original_usd_economy * usd_to_inr_rate
            flight.business_fare = original_usd_business * usd_to_inr_rate if original_usd_business > 0 else 0
            flight.first_fare = original_usd_first * usd_to_inr_rate if original_usd_first > 0 else 0
            
            flight.save()
            
            self.stdout.write(
                f'Fixed Flight ID {flight.id}: '
                f'Economy USD${original_usd_economy:.2f} -> INR{flight.economy_fare:.0f}, '
                f'Business USD${original_usd_business:.2f} -> INR{flight.business_fare:.0f}, '
                f'First USD${original_usd_first:.2f} -> INR{flight.first_fare:.0f}'
            )
            
            fixed_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully fixed {fixed_count} flights!')
        )