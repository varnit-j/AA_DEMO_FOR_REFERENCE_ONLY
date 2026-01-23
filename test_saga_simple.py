#!/usr/bin/env python3
"""
Simple test script to verify SAGA template fix
"""
import requests

def test_saga_results_page():
    """Test that the SAGA results page loads without template errors"""
    print("[TEST] Testing SAGA Results Page...")
    
    try:
        # Test the saga results page with demo parameters
        url = "http://localhost:8000/saga/results?correlation_id=test123&demo=true"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("[PASS] SAGA results page loads successfully (Status: 200)")
            
            # Check if the page contains expected content
            content = response.text
            if "SAGA Transaction Failed" in content:
                print("[PASS] Page contains expected SAGA failure content")
            if "Compensation" in content:
                print("[PASS] Page contains compensation information")
            if "correlation_id" in content.lower():
                print("[PASS] Page displays correlation ID")
                
            return True
        else:
            print(f"[FAIL] SAGA results page failed with status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing SAGA results page: {e}")
        return False

def main():
    """Run the test"""
    print("Starting SAGA Fix Verification Test")
    print("=" * 40)
    
    # Test the SAGA Results Page Template Fix
    result = test_saga_results_page()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    
    if result:
        print("[SUCCESS] SAGA template fix is working correctly!")
        print("The Django template syntax error has been resolved.")
    else:
        print("[FAILED] SAGA template still has issues.")
    
    return result

if __name__ == "__main__":
    main()