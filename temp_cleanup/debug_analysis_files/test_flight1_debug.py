#!/usr/bin/env python3
"""
Debug script to trace why flight1 data is missing in book.html
"""
import requests
import sys
import json
from urllib.parse import urlencode

# Configuration
BACKEND_URL = "http://localhost:8001"
UI_URL = "http://localhost:8000"

print("\n" + "="*70)
print("DEBUGGING: Flight1 Data Missing Issue")
print("="*70 + "\n")

# Step 1: Check backend has flights
print("[1] Checking backend for flights...")
try:
    # Use a valid flight ID (flights are loaded starting from 25317)
    flight_id = 25317
    response = requests.get(f"{BACKEND_URL}/api/flights/{flight_id}/", timeout=5)
    if response.status_code == 200:
        flight_data = response.json()
        print(f"    ✓ Flight 1 found on backend")
        print(f"    - Airline: {flight_data.get('airline', 'N/A')}")
        print(f"    - Flight: {flight_data.get('flight_number', 'N/A')}")
        print(f"    - Price: {flight_data.get('economy_fare', 'N/A')}")
    else:
        print(f"    ✗ Backend returned HTTP {response.status_code}")
        print(f"    Response: {response.text[:100]}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Backend is unreachable: {e}")
    sys.exit(1)

# Step 2: Simulate calling review() endpoint with GET params
print("\n[2] Simulating review() call with GET params...")
try:
    params = {
        'flight1Id': '25317',
        'flight1Date': '22-01-2026',
        'seatClass': 'economy'
    }
    
    print(f"    - Params: {params}")
    
    response = requests.get(
        f"{UI_URL}/review",
        params=params,
        timeout=5,
        allow_redirects=False
    )
    
    print(f"    - Status: HTTP {response.status_code}")
    
    if response.status_code == 302:
        print(f"    ✗ Redirected to: {response.headers.get('Location', 'unknown')}")
        print(f"    (This usually means login is required)")
        sys.exit(1)
    
    if response.status_code == 200:
        html = response.text
        
        # Check for flight1 in HTML
        if 'name="flight1"' in html:
            print(f"    ✓ Found hidden input 'flight1' in HTML")
        else:
            print(f"    ✗ Missing hidden input 'flight1' in HTML")
        
        # Check for error message
        if 'No flight data available' in html:
            print(f"    ✗ Error message found: 'No flight data available'")
            print(f"    - This means flight1 is NOT in the template context")
        else:
            print(f"    ✓ No error message found")
        
        # Check for SAGA section
        if 'saga-demo-section' in html or 'SAGA' in html:
            print(f"    ✓ SAGA section found in HTML")
        else:
            print(f"    ✗ SAGA section NOT found in HTML")
            print(f"    - This could be because flight1 context is missing")
        
        # Check for debug messages in form
        if 'DEBUG' in html:
            print(f"    ✓ Found DEBUG messages")
            # Extract lines with DEBUG
            for line in html.split('\n'):
                if 'DEBUG' in line:
                    print(f"      - {line.strip()[:80]}")
    else:
        print(f"    ✗ Unexpected status: {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        
except Exception as e:
    print(f"    ✗ Error calling review(): {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70 + "\n")

print("INTERPRETATION:")
print("  - If 'No flight data available' appears: flight1 not in context")
print("  - If hidden input 'flight1' exists: flight1 IS in context")
print("  - If SAGA section missing: flight1 conditional failed")
print("\nNEXT STEPS:")
print("  1. Check UI service logs for [DEBUG] SAGA TOGGLE messages")
print("  2. Check if call_backend_api() is returning None")
print("  3. Check if backend is actually responding to /api/flights/1/")
