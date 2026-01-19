
from django.core.management.base import BaseCommand
from flight.models import Flight, Place, Week
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Add American Airlines flights for DFW-ORD and ORD-DFW routes'

    def handle(self, *args, **options):
        self.stdout.write('Adding American Airlines flights...')
        
        try:
            # Get places
            dfw = Place.objects.get(code='DFW')
            ord = Place.objects.get(code='ORD')
            self.stdout.write(f'Found places: {dfw} and {ord}')
            
            # Get all week days (0=Monday, 6=Sunday)
            all_days = Week.objects.all()
            self.stdout.write(f'Found {all_days.count()} week days')
            
            # Flight data from user
            flights_data = [
                # ORD to DFW flights
                {
                    'flight_number': 'AA1838',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(5, 5),
                    'arrival_time': time(7, 40),
                    'price': 150,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA2113',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(6, 54),
                    'arrival_time': time(9, 29),
                    'price': 160,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA2156',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(8, 10),
                    'arrival_time': time(10, 45),
                    'price': 170,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA1213',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(10, 19),
                    'arrival_time': time(12, 54),
                    'price': 180,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA1362',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(15, 23),
                    'arrival_time': time(17, 58),
                    'price': 200,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA2544',
                    'origin': ord,
                    'destination': dfw,
                    'depart_time': time(18, 55),
                    'arrival_time': time(21, 30),
                    'price': 220,
                    'plane': 'Boeing 737-800'
                },
                # DFW to ORD flights
                {
                    'flight_number': 'AA328',
                    'origin': dfw,
                    'destination': ord,
                    'depart_time': time(8, 9),
                    'arrival_time': time(10, 42),
                    'price': 150,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA328B',  # Modified to avoid duplicate
                    'origin': dfw,
                    'destination': ord,
                    'depart_time': time(13, 0),
                    'arrival_time': time(15, 33),
                    'price': 170,
                    'plane': 'Boeing 737-800'
                },
                {
                    'flight_number': 'AA328C',  # Modified to avoid duplicate
                    'origin': dfw,
                    'destination': ord,
                    'depart_time': time(20, 0),
                    'arrival_time': time(22, 33),
                    'price': 200,
                    'plane': 'Boeing 737-800'
                }
            ]
            
            flights_created = 0
            
            for flight_data in flights_data:
                # Calculate duration
                depart_datetime = timedelta(hours=flight_data['depart_time'].hour,
                                          minutes=flight_data['depart_time'].minute)
                arrival_datetime = timedelta(hours=flight_data['arrival_time'].hour,
                                           minutes=flight_data['arrival_time'].minute)
                
                # Handle overnight flights
                if arrival_datetime < depart_datetime:
                    arrival_datetime += timedelta(days=1)
                
                duration = arrival_datetime - depart_datetime
                
                # Store prices in USD (consistent with existing flights)
                economy_fare_usd = flight_data['price']
                business_fare_usd = flight_data['price'] * 2.5
                first_fare_usd = flight_data['price'] * 4.0
                
                print(f"Storing flight prices in USD: Economy=${economy_fare_usd}, Business=${business_fare_usd}, First=${first_fare_usd}")
                
                # Create flight
                flight = Flight.objects.create(
                    origin=flight_data['origin'],
                    destination=flight_data['destination'],
                    depart_time=flight_data['depart_time'],
                    arrival_time=flight_data['arrival_time'],
                    duration=duration,
                    plane=flight_data['plane'],
                    airline='American Airlines',
                    flight_number=flight_data['flight_number'],  # Store flight number
                    economy_fare=economy_fare_usd,
                    business_fare=business_fare_usd,  # Business is 2.5x economy
                    first_fare=first_fare_usd     # First is 4x economy
                )
                
                # Add all days of the week (daily flights)
                flight.depart_day.set(all_days)
                
                flights_created += 1
                self.stdout.write(f'Created flight {flight_data["flight_number"]}: {flight_data["origin"]} -> {flight_data["destination"]} at {flight_data["depart_time"]}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added {flights_created} American Airlines flights!')
            )
            
        except Place.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Place not found: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error adding flights: {e}')
            )