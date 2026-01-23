import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from flight.models import Place, Flight
from datetime import datetime, time


class Command(BaseCommand):
    help = 'Import flight data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='flights_export_20260121_195421.csv',
            help='Path to the CSV file (default: flights_export_20260121_195421.csv)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing flight and place data before import'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        # If relative path, look in current directory
        if not os.path.isabs(csv_file):
            csv_file = os.path.join(os.getcwd(), csv_file)
        
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')

        self.stdout.write(f'Importing flights from: {csv_file}')
        
        if options['clear_existing']:
            self.stdout.write('Clearing existing data...')
            with transaction.atomic():
                Flight.objects.all().delete()
                Place.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        try:
            with transaction.atomic():
                self.import_flights(csv_file)
        except Exception as e:
            raise CommandError(f'Import failed: {str(e)}')

    def import_flights(self, csv_file):
        place_cache = {}
        flights_created = 0
        places_created = 0
        errors = 0

        with open(csv_file, 'r', encoding='utf-8') as file:
            # Skip the header row
            next(file)
            reader = csv.reader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    if len(row) < 19:  # Minimum required columns
                        self.stdout.write(
                            self.style.WARNING(f'Row {row_num}: Insufficient columns, skipping')
                        )
                        continue

                    # Parse CSV columns
                    flight_id = row[0]
                    flight_number = row[1]
                    airline = row[2]
                    plane = row[3]
                    origin_city = row[4]
                    origin_airport = row[5]
                    origin_code = row[6]
                    origin_country = row[7]
                    dest_city = row[8]
                    dest_airport = row[9]
                    dest_code = row[10]
                    dest_country = row[11]
                    depart_time_str = row[12]
                    arrival_time_str = row[13]
                    duration_hours = row[14]
                    operating_days = row[15]
                    economy_fare = row[16]
                    business_fare = row[17] if len(row) > 17 else economy_fare
                    first_fare = row[18] if len(row) > 18 else business_fare

                    # Create or get origin place
                    origin_key = f"{origin_city}_{origin_code}"
                    if origin_key not in place_cache:
                        origin_place, created = Place.objects.get_or_create(
                            city=origin_city,
                            code=origin_code,
                            defaults={
                                'airport': origin_airport,
                                'country': origin_country
                            }
                        )
                        place_cache[origin_key] = origin_place
                        if created:
                            places_created += 1
                    else:
                        origin_place = place_cache[origin_key]

                    # Create or get destination place
                    dest_key = f"{dest_city}_{dest_code}"
                    if dest_key not in place_cache:
                        dest_place, created = Place.objects.get_or_create(
                            city=dest_city,
                            code=dest_code,
                            defaults={
                                'airport': dest_airport,
                                'country': dest_country
                            }
                        )
                        place_cache[dest_key] = dest_place
                        if created:
                            places_created += 1
                    else:
                        dest_place = place_cache[dest_key]

                    # Parse times
                    try:
                        depart_time = datetime.strptime(depart_time_str, '%H:%M').time()
                    except ValueError:
                        depart_time = time(8, 0)  # Default 8:00 AM

                    try:
                        arrival_time = datetime.strptime(arrival_time_str, '%H:%M').time()
                    except ValueError:
                        arrival_time = time(10, 0)  # Default 10:00 AM

                    # Parse fares
                    try:
                        economy_fare = float(economy_fare) if economy_fare else 299.99
                        business_fare = float(business_fare) if business_fare else economy_fare * 2
                        first_fare = float(first_fare) if first_fare else business_fare * 1.5
                    except ValueError:
                        economy_fare = 299.99
                        business_fare = 599.99
                        first_fare = 999.99

                    # Create flight
                    flight, created = Flight.objects.get_or_create(
                        origin=origin_place,
                        destination=dest_place,
                        depart_time=depart_time,
                        airline=airline,
                        defaults={
                            'plane': plane,
                            'arrival_time': arrival_time,
                            'duration': duration_hours,
                            'economy_fare': economy_fare,
                            'business_fare': business_fare,
                            'first_fare': first_fare
                        }
                    )

                    if created:
                        flights_created += 1

                    # Progress indicator
                    if row_num % 1000 == 0:
                        self.stdout.write(f'Processed {row_num} rows...')

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.WARNING(f'Row {row_num}: Error - {str(e)}')
                    )
                    continue

        # Final statistics
        self.stdout.write(self.style.SUCCESS(
            f'\nImport completed successfully!'
        ))
        self.stdout.write(f'Places created: {places_created}')
        self.stdout.write(f'Flights created: {flights_created}')
        self.stdout.write(f'Errors: {errors}')
        self.stdout.write(f'Total places in database: {Place.objects.count()}')
        self.stdout.write(f'Total flights in database: {Flight.objects.count()}')