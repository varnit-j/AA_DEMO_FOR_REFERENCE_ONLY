#!/usr/bin/env python3
"""
Test script to simulate complete user SAGA demo flow
"""
import requests
import json
import time

def test_saga_demo_user_flow():
    """Test the complete user flow: SAGA demo button → failure → results page"""
    print("[TEST] Testing complete user SAGA demo flow...")
    
    try:
        # Step 1: Simulate user clicking SAGA demo button with payment failure
        print("[STEP 1] Simulating SAGA demo with payment failure...")
        
        # This simulates the form submission from the booking page
        booking_data = {
            'flight1': '1',  # This will fail because flight 1 doesn't exist
            'user_id': 1,
            'passengers': [{'first_name': 'Demo', 'last_name': 'User', 'gender': 'male'}],
            'contact_info': {'email': 'demo@example.com', 'mobile': '1234567890'},
            'saga_demo_mode': 'true',
            'simulate_authorizepayment_fail': 'on'  # Simulate payment failure
        }
        
        # Call the UI service book endpoint (this is what happens when user clicks demo)
        book_url = "http://localhost:8000/flight/ticket/book"
        response = requests.post(book_url, data=booking_data, timeout=30, allow_redirects=False)
        
        print(f"[INFO] Book endpoint response: {response.status_code}")
        
        if response.status_code == 302:  # Redirect to results page
            redirect_url = response.headers.get('Location', '')
            print(f"[PASS] Redirected to: {redirect_url}")
            
            # Extract correlation_id from redirect URL
            if 'correlation_id=' in redirect_url:
                correlation_id = redirect_url.split('correlation_id=')[1].split('&')[0]
                print(f"[INFO] Extracted correlation_id: {correlation_id}")
                
                # Step 2: Follow the redirect to the results page
                print("[STEP 2] Following redirect to SAGA results page...")
                
                if redirect_url.startswith('/'):
                    full_results_url = f"http://localhost:8000{redirect_url}"
                else:
                    full_results_url = redirect_url
                
                results_response = requests.get(full_results_url, timeout=10)
                
                if results_response.status_code == 200:
                    print(f"[PASS] SAGA results page loads successfully")
                    
                    content = results_response.text
                    
                    # Check if page contains expected elements
                    checks = [
                        ("SAGA Transaction Failed", "failure header"),
                        ("Correlation ID", "correlation ID display"),
                        ("Real System Logs", "logs section"),
                        ("Transaction Summary", "summary section"),
                        ("Compensation", "compensation info"),
                        (correlation_id, "actual correlation ID")
                    ]
                    
                    all_passed = True
                    for check_text, description in checks:
                        if check_text in content:
                            print(f"[PASS] Page contains {description}")
                        else:
                            print(f"[FAIL] Page missing {description}")
                            all_passed = False
                    
                    return all_passed
                else:
                    print(f"[FAIL] SAGA results page failed: {results_response.status_code}")
                    return False
            else:
                print(f"[FAIL] No correlation_id in redirect URL: {redirect_url}")
                return False
        else:
            print(f"[FAIL] Expected redirect but got: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing user SAGA flow: {e}")
        return False

def main():
    """Run the complete user flow test"""
    print("=" * 60)
    print("USER SAGA DEMO FLOW TEST")
    print("=" * 60)
    
    result = test_saga_demo_user_flow()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    
    if result:
        print("[SUCCESS] Complete user SAGA flow test passed!")
        print("✓ SAGA demo button simulation works")
        print("✓ Failure scenario triggers correctly")
        print("✓ Results page displays properly")
        print("✓ All expected content is present")
    else:
        print("[FAILED] User SAGA flow test failed")
        print("Check the logs above for details")
    
    return result

if __name__ == "__main__":
    main()