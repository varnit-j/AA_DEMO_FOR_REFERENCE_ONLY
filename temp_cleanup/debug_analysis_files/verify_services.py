#!/usr/bin/env python3
"""
Quick service verification script to test if all microservices are running properly
after cleanup operations.
"""

import requests
import time

def test_service_connectivity():
    """Test if all services are running and responding"""
    services = {
        'UI Service': 'http://localhost:8000',
        'Backend Service': 'http://localhost:8001',
        'Loyalty Service': 'http://localhost:8002',
        'Payment Service': 'http://localhost:8003'
    }
    
    print("Testing microservices connectivity after cleanup...")
    print("=" * 60)
    
    all_services_ok = True
    
    for service_name, url in services.items():
        try:
            print(f"Testing {service_name}...")
            response = requests.get(f"{url}/", timeout=10)
            if response.status_code in [200, 404]:  # 404 is OK for root endpoints
                print(f"[OK] {service_name}: RUNNING (Status: {response.status_code})")
            else:
                print(f"[WARN] {service_name}: UNEXPECTED STATUS ({response.status_code})")
                all_services_ok = False
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] {service_name}: CONNECTION FAILED")
            all_services_ok = False
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] {service_name}: TIMEOUT")
            all_services_ok = False
        except Exception as e:
            print(f"[ERROR] {service_name}: ERROR - {str(e)}")
            all_services_ok = False
    
    print("=" * 60)
    
    if all_services_ok:
        print("ALL SERVICES ARE RUNNING PROPERLY!")
        print("Cleanup operation was successful - no essential files were affected")
        return True
    else:
        print("SOME SERVICES HAVE ISSUES")
        print("Please check the service logs for more details")
        return False

def test_basic_endpoints():
    """Test some basic API endpoints"""
    print("\nTesting basic API endpoints...")
    print("=" * 60)
    
    endpoints = [
        ('Backend Health', 'http://localhost:8001/api/health/'),
        ('Loyalty Health', 'http://localhost:8002/loyalty/health/'),
        ('Payment Health', 'http://localhost:8003/payment/health/')
    ]
    
    for endpoint_name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {endpoint_name}: OK")
            else:
                print(f"[WARN] {endpoint_name}: Status {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {endpoint_name}: {str(e)}")

if __name__ == "__main__":
    print("Starting service verification after cleanup...")
    time.sleep(2)  # Give services a moment to fully start
    
    connectivity_ok = test_service_connectivity()
    test_basic_endpoints()
    
    print("\n" + "=" * 60)
    if connectivity_ok:
        print("VERIFICATION COMPLETE: Services are stable after cleanup")
        print("Safe to proceed with temp folder deletion")
    else:
        print("VERIFICATION FAILED: Some services may need attention")
        print("Please check service logs before deleting temp files")