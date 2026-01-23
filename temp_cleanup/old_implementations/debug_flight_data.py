
#!/usr/bin/env python3
"""
Quick Debug Script for Flight1 Data Issue
"""

import requests
import json

def test_flight_data():
    print("🔍 Debugging Flight1 Data Issue...")
    
    # Test 1: Check if backend service has flights
    print("\n1. Testing Backend Service Flight Data...")
    try:
        response = requests.get("http://localhost:8001/api/flights/search/", params={
            'origin': 'New York',
            'destination': 'Los Angeles', 
            'trip_type': '1',
            'depart_date': '2026-01-25',
            'seat_class': 'economy'
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            flights = data.get('flights', [])
            print(f"✅ Backend has {len(flights)} flights")
            if flights:
                first_flight = flights[0]
                flight_id = first_flight.get('id')
                print(f"   First flight ID: {flight_id}")
                print(f"   First flight airline: {first_flight.get('airline', 'Unknown')}")
                return flight_id
        else:
            print(f"❌ Backend search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
    
    return None

def test_review_page(flight_id):
    print(f"\n2. Testing Review Page with Flight ID: {flight_id}")
    
    if not flight_id:
        print("❌ No flight ID to test with")
        return
    
    # Test review page with flight data
    try:
        response = requests.get("http://localhost:8000/review", params={
            'flight1Id': flight_id,
            'flight1Date': '2026-01-25',
            'seatClass': 'economy'
        }, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if 'DEBUG: No flight1 data' in content:
                print("❌ Review page shows 'No flight1 data' error")
                print("   This means the UI service can't fetch flight data from backend")
            elif 'flight1' in content:
                print("✅ Review page has flight1 data")
            else:
                print("⚠️ Review page loaded but flight1 status unclear")
        else:
            print(f"❌ Review page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Review page connection error: {e}")

def test_direct_flight_api(flight_id):
    print(f"\n3. Testing Direct Flight API with ID: {flight_id}")
    
    if not flight_id:
        return
    
    try:
        response = requests.get(f"http://localhost:8001/api/flights/{flight_id}/", timeout=10)
        if response.status_code == 200:
            flight_data = response.json()
            print("✅ Direct flight API works")
            print(f"   Airline: {flight_data.get('airline', 'Unknown')}")
            print(f"   Origin: {flight_data.get('origin', 'Unknown')}")
            print(f"   Destination: {flight_data.get('destination', 'Unknown')}")
        else:
            print(f"❌ Direct flight API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct flight API error: {e}")

def test_ui_backend_connection():
    print("\n4. Testing UI Service Backend Connection...")
    
    # Check if UI service can connect to backend
    try:
        # Test the flight search endpoint that UI service uses
        response = requests.get("http://localhost:8000/flight", params={
            'Origin': 'New York',
            'Destination': 'Los Angeles',
            'TripType': '1',
            'DepartDate': '2026-01-25',
            'SeatClass': 'economy'
        }, timeout=10)
        
        if response.status_code == 200:
            print("✅ UI service flight search works")
        else:
            print(f"❌ UI service flight search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ UI service connection error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Flight Data Debug...")
    
    # Run all tests
    flight_id = test_flight_data()
    test_review_page(flight_id)
    test_direct_flight_api(flight_id)
    test_ui_backend_connection()
    
    print("\n📋 Debug Summary:")
    print("If you see 'No flight1 data' error, the issue is likely:")
    print("1. Backend service not returning flight data properly")
    print("2. UI service can't connect to backend service")
    print("3. Flight ID parameter not being passed correctly")
    print("4. Backend service URL configuration issue in UI service")