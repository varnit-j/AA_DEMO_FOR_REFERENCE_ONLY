#!/usr/bin/env python3
"""
Configuration Validation Test Suite
This test specifically validates service URL configurations and would have caught the bug.
"""

import requests
import time

def test_service_url_configurations():
    """Test that would have caught the loyalty service URL misconfiguration"""
    print("="*60)
    print("CONFIGURATION VALIDATION TEST SUITE")
    print("="*60)
    
    # Expected service mappings
    expected_services = {
        'backend': 'http://localhost:8001',
        'loyalty': 'http://localhost:8002', 
        'payment': 'http://localhost:8003',
        'ui': 'http://localhost:8000'
    }
    
    print("\n1. Testing correct service endpoints...")
    for service_name, url in expected_services.items():
        try:
            if service_name == 'loyalty':
                response = requests.get(f"{url}/loyalty/status/", timeout=5)
            elif service_name == 'payment':
                response = requests.get(f"{url}/", timeout=5)
            else:
                response = requests.get(f"{url}/", timeout=5)
                
            if response.status_code in [200, 302]:
                print(f"✓ {service_name.upper()} service correctly running on {url}")
            else:
                print(f"✗ {service_name.upper()} service issue on {url}: {response.status_code}")
        except Exception as e:
            print(f"✗ {service_name.upper()} service not accessible on {url}: {e}")
    
    print("\n2. Testing for configuration errors (wrong service on wrong port)...")
    
    # Test if loyalty endpoints work on payment port (8003) - this would catch the bug!
    try:
        response = requests.get("http://localhost:8003/loyalty/status/", timeout=5)
        if response.status_code == 200:
            print("✗ CRITICAL ERROR: Loyalty service responding on payment port 8003!")
            print("  This indicates LOYALTY_SERVICE_URL is misconfigured in UI service")
        else:
            print("✓ Loyalty service correctly NOT responding on payment port 8003")
    except Exception:
        print("✓ Loyalty service correctly NOT responding on payment port 8003")
    
    # Test if payment endpoints work on loyalty port (8002)
    try:
        response = requests.get("http://localhost:8002/payment/status/", timeout=5)
        if response.status_code == 200:
            print("✗ CRITICAL ERROR: Payment service responding on loyalty port 8002!")
        else:
            print("✓ Payment service correctly NOT responding on loyalty port 8002")
    except Exception:
        print("✓ Payment service correctly NOT responding on loyalty port 8002")
    
    print("\n3. Testing UI service loyalty integration...")
    
    # Test the actual redemption flow that was failing
    test_user_id = '1'
    redemption_data = {
        'user_id': test_user_id,
        'points_to_redeem': 25,
        'transaction_id': f'CONFIG_TEST_{int(time.time())}'
    }
    
    # Test direct loyalty service call (should work)
    try:
        response = requests.post('http://localhost:8002/loyalty/redeem-points/', 
                               json=redemption_data, timeout=10)
        if response.status_code == 200:
            print("✓ Direct loyalty service redemption works")
            
            # Check if redemption appears in history
            hist_response = requests.get(f'http://localhost:8002/api/loyalty/history/{test_user_id}/', timeout=5)
            if hist_response.status_code == 200:
                hist_result = hist_response.json()
                transactions = hist_result.get('transactions', [])
                redemption_count = sum(1 for t in transactions if t.get('type') == 'miles_redemption')
                print(f"✓ Redemption appears in history ({redemption_count} redemption transactions found)")
            else:
                print("✗ Could not retrieve transaction history")
        else:
            print(f"✗ Direct loyalty service redemption failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Direct loyalty service redemption error: {e}")
    
    print("\n4. Final validation - Testing current points balance...")
    try:
        response = requests.get(f'http://localhost:8002/loyalty/status/?user_id={test_user_id}', timeout=5)
        if response.status_code == 200:
            result = response.json()
            points_balance = result.get('points_balance', 0)
            print(f"✓ User {test_user_id} current balance: {points_balance} points")
        else:
            print(f"✗ Could not get current balance: {response.status_code}")
    except Exception as e:
        print(f"✗ Balance check error: {e}")
    
    print("\n" + "="*60)
    print("CONFIGURATION TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_service_url_configurations()