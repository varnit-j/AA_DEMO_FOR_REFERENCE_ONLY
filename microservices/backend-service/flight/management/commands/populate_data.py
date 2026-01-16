
import csv
import os
from datetime import time, timedelta
from django.core.management.base import BaseCommand
from flight.models import Place, Week, Flight


class Command(BaseCommand):
    help = 'Populate database with flight data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write('Starting data population...')
        
        # Create Week objects
        self.create_weeks()
        
        # Load places from CSV
        self.load_places()
        
        # Load flights from CSV
        self.load_flights()
        
        self.stdout.write(self.style.SUCCESS('Data population completed!'))

    def create_weeks(self):
        """Create Week objects for days of the week"""
        weeks = [
            (0, 'Monday'),
            (1, 'Tuesday'), 
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday')
        ]
        
        for number, name in weeks:
            week, created = Week.objects.get_or_create(number=number, name=name)
            if created:
                self.stdout.write(f'Created week: {name}')

    def load_places(self):
        """Load places from airports.csv"""
        csv_path = os.path.join('..', '..', 'Data', 'airports.csv')
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.WARNING(f'CSV file not found: {csv_path}'))
            # Create some basic places for testing
            self.create_basic_places()
            return
            
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                place, created = Place.objects.get_or_create(
                    code=row['code'].upper(),
                    defaults={
                        'city': row['city'],
                        'airport': row['airport'],
                        'country': row['country']
                    }
                )
                if created:
                    self.stdout.write(f'Created place: {place}')

    def create_basic_places(self):
        """Create basic places for testing"""
        places = [
            {'city': 'Delhi', 'airport': 'Indira Gandhi International Airport', 'code': 'DEL', 'country': 'India'},
            {'city': 'Mumbai', 'airport': 'Chhatrapati Shivaji International Airport', 'code': 'BOM', 'country': 'India'},
            {'city': 'Bangalore', 'airport': 'Kempegowda International Airport', 'code': 'BLR', 'country': 'India'},
            {'city': 'Chennai', 'airport': 'Chennai International Airport', 'code': 'MAA', 'country': 'India'},
            {'city': 'Kolkata', 'airport': 'Netaji Subhas Chandra Bose International Airport', 'code': 'CCU', 'country': 'India'},
            {'city': 'Hyderabad', 'airport': 'Rajiv Gandhi International Airport', 'code': 'HYD', 'country': 'India'},
        ]
        
        for place_data in places:
            place, created = Place.objects.get_or_create(
                code=place_data['code'],
                defaults=place_data
            )
            if created:
                self.stdout.write(f'Created place: {place}')

    def load_flights(self):
        """Create sample flights for testing"""
        self.create_sample_flights()

    def create_sample_flights(self):
        """Create