#!/usr/bin/env python3
"""
Transfer flight data from the CSV-generated database to the backend service database
"""
import sqlite3
import os
import sys

def transfer_flight_data():
    """Transfer flight data from test_flights.db to backend service database"""
    
    # Paths
    source_db = "AA_Flight_booking/Data/test_flights.db"
    target_db = "AA_Flight_booking/microservices/backend-service/db.sqlite3"
    
    if not os.path.exists(source_db):
        print(f"ERROR: Source database not found: {source_db}")
        return False
    
    if not os.path.exists(target_db):
        print(f"ERROR: Target database not found: {target_db}")
        print("Make sure the backend service has been started and migrations have been run.")
        return False
    
    try:
        # Connect to both databases
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        print("Connected to both databases successfully")
        
        # Get all flights from source database
        source_cursor.execute("SELECT * FROM flights")
        flights = source_cursor.fetchall()
        
        print(f"Found {len(flights)} flights in source database")
        
        if len(flights) == 0:
            print("No flights found in source database")
            return False
        
        # Get column names from source
        source_cursor.execute("PRAGMA table_info(flights)")
        source_columns = [column[1] for column in source_cursor.fetchall()]
        print(f"Source columns: {source_columns}")
        
        # Check target table structure
        target_cursor.execute("PRAGMA table_info(flight_flight)")
        target_columns = [column[1] for column in target_cursor.fetchall()]
        print(f"Target columns: {target_columns}")
        
        # Clear existing flight data
        target_cursor.execute("DELETE FROM flight_flight")
        target_cursor.execute("DELETE FROM flight_place")
        print("Cleared existing flight and place data")
        
        # Insert places first (extract unique origins and destinations)
        places = set()
        for flight in flights:
            if len(flight) >= 4:  # Make sure we have enough columns
                places.add(flight[1])  # origin
                places.add(flight[2])  # destination
        
        place_id_map = {}
        place_id = 1
        for place in places:
            airport_code = place[:3].upper()
            target_cursor.execute(
                "INSERT INTO flight_place (id, city, airport, code, country) VALUES (?, ?, ?, ?, ?)",
                (place_id, place, f"{place} Airport", airport_code, "US")
            )
            place_id_map[place] = place_id
            place_id += 1
        
        print(f"Inserted {len(places)} places")
        
        # Insert flights
        flight_count = 0
        for flight in flights:
            if len(flight) >= 8:  # Make sure we have all required columns
                try:
                    origin_id = place_id_map.get(flight[1])
                    destination_id = place_id_map.get(flight[2])
                    
                    if origin_id and destination_id:
                        target_cursor.execute("""
                            INSERT INTO flight_flight
                            (id, origin_id, destination_id, plane, depart_time,
                             arrival_time, economy_fare, business_fare, first_fare, flight_number, airline, duration)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            flight[0],  # id
                            origin_id,  # origin_id
                            destination_id,  # destination_id
                            flight[3] if len(flight) > 3 else "Boeing 737",  # plane
                            flight[6] if len(flight) > 6 else "08:00:00",  # depart_time
                            flight[7] if len(flight) > 7 else "10:00:00",  # arrival_time
                            flight[10] if len(flight) > 10 else 299.99,  # economy_fare
                            flight[11] if len(flight) > 11 else 599.99,  # business_fare
                            flight[12] if len(flight) > 12 else 999.99,  # first_fare
                            flight[1] if len(flight) > 1 else f"AA{flight_count + 1000}",  # flight_number
                            flight[2] if len(flight) > 2 else "American Airlines",  # airline
                            flight[8] if len(flight) > 8 else "2:00"  # duration_hours
                        ))
                        flight_count += 1
                        
                        if flight_count % 1000 == 0:
                            print(f"Inserted {flight_count} flights...")
                            
                except Exception as e:
                    print(f"Error inserting flight {flight[0]}: {e}")
                    continue
        
        # Commit changes
        target_conn.commit()
        print(f"Successfully transferred {flight_count} flights")
        
        # Close connections
        source_conn.close()
        target_conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Flight Data Transfer Tool")
    print("=" * 40)
    
    success = transfer_flight_data()
    if success:
        print("Transfer completed successfully!")
        print("You can now search for flights in the application.")
    else:
        print("Transfer failed. Please check the error messages above.")