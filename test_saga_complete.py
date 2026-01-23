#!/usr/bin/env python3
"""
Comprehensive test script to verify SAGA results page displays complete data
"""
import requests
import re

def test_saga_results_content():
    """Test that the SAGA results page displays proper correlation ID and logs"""
    print("[TEST] Testing SAGA Results Page Content...")
    
    try:
        # Test the saga results page with demo parameters
        url = "http://localhost:8000/saga/results?correlation_id=unknown&demo=true"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("[PASS] SAGA results page loads successfully (Status: 200)")
            
            content = response.text
            
            # Check for correlation ID (should not be "unknown" anymore)
            if "Correlation ID:" in content:
                print("[PASS] Page contains correlation ID section")
                # Extract correlation ID from the content
                correlation_match = re.search(r'Correlation ID:</strong>\s*([a-f0-9-]+)', content)
                if correlation_match:
                    correlation_id = correlation_match.group(1)
                    if correlation_id != "unknown":
                        print(f"[PASS] Generated correlation ID: {correlation_id}")
                    else:
                        print("[FAIL] Correlation ID is still 'unknown'")
                        return False
                else:
                    print("[FAIL] Could not extract correlation ID from page")
                    return False
            else:
                print("[FAIL] Page missing correlation ID section")
                return False
            
            # Check for SAGA transaction logs
            if "Real System Logs" in content:
                print("[PASS] Page contains system logs section")
            else:
                print("[FAIL] Page missing system logs section")
                return False
            
            # Check for specific log entries
            if "ReserveSeat step initiated" in content:
                print("[PASS] Page contains ReserveSeat log entry")
            else:
                print("[FAIL] Page missing ReserveSeat log entry")
                return False
            
            # Check for compensation information
            if "Compensation" in content or "compensation" in content:
                print("[PASS] Page contains compensation information")
            else:
                print("[FAIL] Page missing compensation information")
                return False
            
            # Check for transaction summary
            if "Transaction Summary" in content:
                print("[PASS] Page contains transaction summary")
            else:
                print("[FAIL] Page missing transaction summary")
                return False
            
            # Check for failed step information
            if "Failed Step:" in content:
                print("[PASS] Page contains failed step information")
            else:
                print("[FAIL] Page missing failed step information")
                return False
            
            # Check for steps completed information
            if "Steps Completed:" in content:
                print("[PASS] Page contains steps completed information")
            else:
                print("[FAIL] Page missing steps completed information")
                return False
            
            return True
        else:
            print(f"[FAIL] SAGA results page failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing SAGA results page: {e}")
        return False

def main():
    """Run the comprehensive test"""
    print("Starting SAGA Complete Fix Verification Test")
    print("=" * 50)
    
    # Test the SAGA Results Page Content
    result = test_saga_results_content()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    if result:
        print("[SUCCESS] SAGA results page is now complete!")
        print("- Correlation ID is properly generated")
        print("- System logs are displayed")
        print("- Compensation information is shown")
        print("- Transaction summary is complete")
    else:
        print("[FAILED] SAGA results page still has missing data.")
    
    return result

if __name__ == "__main__":
    main()
        