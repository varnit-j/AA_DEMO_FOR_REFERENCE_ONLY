
"""
Test script for SAGA pattern with seat reservation
Tests the complete flow: ReserveSeat → AuthorizePayment → AwardMiles → ConfirmBooking
"""
import requests
import json
import time

# Service endpoints
BACKEND_SERVICE = "http://localhost:8001"
LOYALTY_SERVICE = "http://localhost:8002"
PAYMENT_SERVICE = "http://localhost:8003"

def test_saga_seat_reservation():
    """Test SAGA pattern with real seat reservation"""
    print("=== Testing SAGA Pattern with Seat Reservation ===")
    
    # Test data
    booking_data = {
        'flight_id': 1,  # Assuming flight ID 1 exists
        'user_id': 1,
        'passengers': [
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female'}
        ],
        'contact_info': {
            'email': 'john@example.com',
            'mobile': '+1234567890'
        },
        'seat_class': 'economy'
    }
    
    print(f"\n1. Testing SAGA booking with {len(booking_data['passengers'])} passengers...")
    
    try:
        # Test the complete SAGA flow
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/start-booking/", json=booking_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Correlation ID: {result.get('correlation_id')}")
            print(f"   Seats Reserved: {result.get('seats_reserved')}")
            print(f"   Seat Numbers: {result.get('seat_numbers')}")
            print(f"   Booking Reference: {result.get('booking_reference')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")

def test_saga_payment_failure():
    """Test SAGA compensation when payment fails"""
    print("\n=== Testing SAGA Compensation (Payment Failure) ===")
    
    booking_data = {
        'flight_id': 1,
        'user_id': 1,
        'passengers': [
            {'first_name': 'Test', 'last_name': 'User', 'gender': 'male'}
        ],
        'contact_info': {
            'email': 'test@example.com',
            'mobile': '+1234567890'
        },
        'seat_class': 'economy',
        'simulate_authorizepayment_fail': True  # Force payment failure
    }
    
    print(f"\n1. Testing SAGA with payment failure simulation...")
    
    try:
        response = requests.post(f"{BACKEND_SERVICE}/api/saga/start-booking/", json=booking_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Error: {result.get('error')}")
            print(f"   Failed Step: {result.get('step')}")
            print(f"   Message: Compensation should have released seats")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")

def test_