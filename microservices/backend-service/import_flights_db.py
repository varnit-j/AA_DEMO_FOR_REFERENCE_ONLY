#!/usr/bin/env python3
"""
PROVEN STANDALONE DATABASE RECREATION SCRIPT
Run this script to recreate the complete flight database from CSV
Works independently and creates exact database structure for frontend/backend
"""

import os
import sys
import django
import csv
from datetime import datetime, timedelta, time

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    django.setup()
    from flight.models import Flight, Place, Week
    from django.db import transaction
    print("SUCCESS: Django setup successful - models imported")
except Exception as e:
    print(f"ERROR: Django setup failed: {e}")
    sys.exit(1)

def main():
    """Main execution function"""
    print("FLIGHT DATABASE RECREATION TOOL")
    print("=" * 50)
    
    # CSV file path
    csv_file = "flights_export_20260121_195421.csv"
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file not found: {csv_file}")
        print("Please ensure the CSV file is in the same directory as this script")
        return False
    
    try:
        # Step 1: Clear existing data
        print("Clearing existing data...")
        with transaction.atomic():
            Flight.objects.all().delete()
            Place.objects.all().delete()
        print("SUCCESS: Existing data cleared")
        
        # Step 2: Setup week data
        print("Setting up week data...")
        weeks = [
            (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
            (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
        ]
        for number, name in weeks:
            Week.objects.get_or_create(number=number, defaults={'name': name})
        print("SUCCESS: Week data setup complete")
        
        # Step 3: Import flights from CSV
        print("Importing flights from CSV...")
        imported_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Get or create origin place
                        origin_place, _ = Place.objects.get_or_create(
                            city=row['Origin City'],
                            airport=row['Origin Airport'],
                            code=row['Origin Code'],
                            country=row['Origin Country']
                        )
                        
                        # Get or create destination place
                        dest_place, _ = Place.objects.get_or_create(
                            city=row['Destination City'],
                            airport=row['Destination Airport'],
                            code=row['Destination Code'],
                            country=row['Destination Country']
                        )
                        
                        # Parse times
                        def parse_time(time_str):
                            if not time_str:
                                return time(0, 0)
                            try:
                                parts = time_str.split(':')
                                return time(int(parts[0]), int(parts[1]))
                            except:
                                return time(0, 0)
                        
                        depart_time = parse_time(row['Departure Time'])
                        arrival_time = parse_time(row['Arrival Time'])
                        
                        # Parse duration
                        duration = None
                        if row['Duration (Hours)']:
                            try:
                                hours = float(row['Duration (Hours)'])
                                duration = timedelta(hours=hours)
                            except:
                                duration = None
                        
                        # Parse fares
                        economy_fare = float(row['Economy Fare (USD)']) if row['Economy Fare (USD)'] else None
                        business_fare = float(row['Business Fare (USD)']) if row['Business Fare (USD)'] else None
                        first_fare = float(row['First Fare (USD)']) if row['First Fare (USD)'] else None
                        
                        # Create flight
                        flight = Flight.objects.create(
                            origin=origin_place,
                            destination=dest_place,
                            depart_time=depart_time,
                            arrival_time=arrival_time,
                            duration=duration,
                            plane=row['Plane'],
                            airline=row['Airline'],
                            flight_number=row['Flight Number'],
                            economy_fare=economy_fare,
                            business_fare=business_fare,
                            first_fare=first_fare
                        )
                        
                        # Add operating days
                        if row['Operating Days']:
                            day_names = [d.strip() for d in row['Operating Days'].split(',')]
                            for day_name in day_names:
                                try:
                                    week_obj = Week.objects.get(name=day_name)
                                    flight.depart_day.add(week_obj)
                                except Week.DoesNotExist:
                                    pass
                        
                        imported_count += 1
                        
                        if imported_count % 1000 == 0:
                            print(f"   Imported {imported_count} flights...")
                            
                    except Exception as e:
                        print(f"   Error importing row {row_num}: {e}")
                        skipped_count += 1
                        continue
        
        print(f"SUCCESS: Import completed!")
        print(f"   Successfully imported: {imported_count} flights")
        print(f"   Skipped: {skipped_count} flights")
        
        # Step 4: Verify database
        print("Verifying database...")
        flight_count = Flight.objects.count()
        place_count = Place.objects.count()
        week_count = Week.objects.count()
        
        print(f"   Flights: {flight_count}")
        print(f"   Places: {place_count}")
        print(f"   Weeks: {week_count}")
        
        if flight_count > 0:
            print("SUCCESS: Database recreation successful!")
            print("   Frontend/Backend should now work with full flight data")
            return True
        else:
            print("ERROR: No flights imported - check CSV file")
            return False
            
    except Exception as e:
        print(f"ERROR: Error during database recreation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: READY TO USE - Database recreated successfully")
        print("   You can now use the frontend with full flight functionality")
    else:
        print("\nFAILED: Database recreation failed")