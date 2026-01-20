
#!/usr/bin/env python3
"""
Integration test to verify data persistence across all services
"""
import requests
import json
import time

def test_service_integration():
    """Test data persistence integration across services"""
    print("=== Testing Data Persistence Integration ===")
    
    # Test data
    test_user_id = "integration_test_user"
    test_amount = 250.0
    test_transaction_id = "INTEGRATION_TEST_001"
    
    print(f"\n1. Testing loyalty service direct API...")
    
    # Test 1: Add points via loyalty service API
    try:
        add_points_data = {
            'user_id': test_user_id,
            'amount': test_amount,
            'transaction_id': test_transaction_id
        }
        
        response = requests.post(
            'http://localhost:8002/loyalty/add-points/',
            json=add_points_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Added {result.get('points_earned', 0)} points via loyalty service")
            print(f"     Total points: {result.get('total_points', 0)}")
        else:
            print(f"[ERROR] Failed to add points: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to loyalty service: {e}")
        return False
    
    # Test 2: Verify points persistence
    print(f"\n2. Testing data persistence...")
    
    try:
        response = requests.get(
            f'http://localhost:8002/loyalty/status/?user_id={test_user_id}',
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            points_balance = result.get('points_balance', 0)
            user_tier = result.get('user_tier', 'Unknown')
            print(f"[OK] Retrieved user status: {points_balance} points, tier: {user_tier}")
            
            if points_balance >= 250:
                print(f"[OK] Points persistence verified")
            else:
                print(f"[ERROR] Points not persisted correctly")
                return False
        else:
            print(f"[ERROR] Failed to get user status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not verify persistence: {e}")
        return False
    
    # Test 3: Test transaction history
    print(f"\n3. Testing transaction history...")
    
    try:
        response = requests.get(
            f'http://localhost:8002/loyalty/transactions/{test_user_id}/',
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            transactions = result.get('transactions', [])
            print(f"[OK] Retrieved {len(transactions)} transactions")
            
            # Check if our test transaction exists
            test_txn_found = False
            for txn in transactions:
                if txn.get('transaction_id') == test_transaction_id:
                    test_txn_found = True
                    print(f"[OK] Test transaction found: {txn.get('points_earned', 0)} points")
                    break
            
            if not test_txn_found:
                print(f"[ERROR] Test transaction not found in history")
                return False
        else:
            print(f"[ERROR] Failed to get transaction history: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not get transaction history: {e}")
        return False
    
    # Test 4: Test points redemption
    print(f"\n4. Testing points redemption...")
    
    try:
        redeem_data = {
            'user_id': test_user_id,
            'points_to_redeem': 100,
            'transaction_id': 'REDEEM_TEST_001'
        }
        
        response = requests.post(
            'http://localhost:8002/loyalty/redeem-points/',
            json=redeem_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            points_redeemed = result.get('points_redeemed', 0)
            remaining_points = result.get('remaining_points', 0)
            print(f"[OK] Redeemed {points_redeemed} points, remaining: {remaining_points}")
        else:
            print(f"[ERROR] Failed to redeem points: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not redeem points: {e}")
        return False
    
    print(f"\n=== Integration Test Summary ===")
    print(f"[SUCCESS] All data persistence tests passed!")
    print(f"- Points addition: Working")
    print(f"- Data persistence: Working")
    print(f"- Transaction history: Working")
    print(f"- Points redemption: Working")
    print(f"- Database storage: Persistent across requests")
    
    return True

if __name__ == '__main__':
    success = test_service_integration()
    if success:
        print(f"\n[FINAL] Data persistence implementation is complete and working!")
    else:
        print(f"\n[FINAL] Some tests failed - check service connectivity")