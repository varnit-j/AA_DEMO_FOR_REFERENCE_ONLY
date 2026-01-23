#!/usr/bin/env python3
"""
Comprehensive test for points redemption flow and miles history tracking
Tests the complete flow from adding points to redemption to history verification
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
LOYALTY_SERVICE_URL = 'http://localhost:8002'
UI_SERVICE_URL = 'http://localhost:8000'

def test_service_connectivity():
    """Test if all services are running"""
    print("=" * 60)
    print("TESTING SERVICE CONNECTIVITY")
    print("=" * 60)
    
    services = {
        'Loyalty Service': f'{LOYALTY_SERVICE_URL}/loyalty/status/',
        'UI Service': f'{UI_SERVICE_URL}/'
    }
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {service_name}: ONLINE (Status: {response.status_code})")
            else:
                print(f"✗ {service_name}: ISSUE (Status: {response.status_code})")
        except Exception as e:
            print(f"✗ {service_name}: OFFLINE - {e}")
    print()

def create_test_user_with_points():
    """Create a test user with initial points for redemption testing"""
    print("=" * 60)
    print("CREATING TEST USER WITH INITIAL POINTS")
    print("=" * 60)
    
    user_id = "test_user_123"
    
    # Step 1: Add initial points via flight booking simulation
    print(f"Step 1: Adding initial points for user {user_id}")
    add_points_data = {
        'user_id': user_id,
        'amount': 500.00,  # $500 flight = 500 points
        'transaction_id': f'FLIGHT_BOOKING_{int(time.time())}'
    }
    
    try:
        response = requests.post(
            f'{LOYALTY_SERVICE_URL}/loyalty/add-points/',
            json=add_points_data,
            timeout=10
        )
        
        print(f"Request URL: {LOYALTY_SERVICE_URL}/loyalty/add-points/")
        print(f"Request Data: {add_points_data}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully added {result.get('points_earned', 0)} points")
            print(f"✓ Total points balance: {result.get('total_points', 0)}")
            return user_id, result.get('total_points', 0)
        else:
            print(f"✗ Failed to add points: {response.status_code} - {response.text}")
            return None, 0
            
    except Exception as e:
        print(f"✗ Error adding points: {e}")
        return None, 0

def test_points_redemption(user_id, available_points):
    """Test points redemption functionality"""
    print("=" * 60)
    print("TESTING POINTS REDEMPTION")
    print("=" * 60)
    
    if available_points < 100:
        print(f"✗ Insufficient points for redemption test. Available: {available_points}, Required: 100")
        return False
    
    # Test redemption of 100 points
    points_to_redeem = 100
    redemption_data = {
        'user_id': user_id,
        'points_to_redeem': points_to_redeem,
        'transaction_id': f'REDEMPTION_{int(time.time())}'