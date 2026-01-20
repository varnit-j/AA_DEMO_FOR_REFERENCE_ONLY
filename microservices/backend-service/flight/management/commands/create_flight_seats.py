"""
Management command to create seats for all flights
Creates 162 seats per flight: Economy (1A-27F), Business (1A-3F), First (1A-2F)
"""
from django.core.management.base import BaseCommand
from flight.models import Flight, Seat

class Command(BaseCommand):
    help = 'Create seats for all flights'

    def handle(self, *args, **options):
        flights = Flight.objects.all()
        
        for flight in flights:
            # Check if seats already exist
            if flight.seats.exists():
                self.stdout.write(f"Seats already exist for {flight.flight_number}")
                continue
            
            seats_created = 0
            
            # Create Economy seats (1A-27F = 162 seats)
            for row in range(1, 28):  # Rows 1-27
                for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                    seat_number = f"{row}{seat_letter}"
                    Seat.objects.create(
                        flight=flight,
                        seat_number=seat_number,
                        seat_class='economy'
                    )
                    seats_created += 1
            
            # Create Business seats (1A-3F = 18 seats) - Override first 3 rows
            for row in range(1, 4):  # Rows 1-3
                for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                    seat_number = f"{row}{seat_letter}"
                    # Update existing economy seats to business
                    Seat.objects.filter(
                        flight=flight, 
                        seat_number=seat_number
                    ).update(seat_class='business')
            
            # Create First class seats (1A-2F = 12 seats) - Override first 2 rows
            for row in range(1, 3):  # Rows 1-2
                for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                    seat_number = f"{row}{seat_letter}"
                    # Update existing seats to first class
                    Seat.objects.filter(
                        flight=flight, 
                        seat_number=seat_number
                    ).update(seat_class='first')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {seats_created} seats for {flight.flight_number}"
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Seat creation completed for {flights.count()} flights"
            )
        )