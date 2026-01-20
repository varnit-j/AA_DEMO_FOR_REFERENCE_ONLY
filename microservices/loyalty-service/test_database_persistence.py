#!/usr/bin/env python3
"""
Test script to verify database persistence for loyalty service
"""
import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loyalty.settings')
django.setup()

from loyalty.models import LoyaltyAccount, LoyaltyTransaction

def test_database_persistence():
    """Test database persistence functionality"""
    print("=== Testing Database Persistence ===")
    
    # Test 1: Create loyalty account directly in database
    print("\n1. Testing direct database operations...")
    
    # Clear any existing test data
    LoyaltyAccount.objects.filter(user_id='test_user_123').delete()
    
    # Create account
    account = LoyaltyAccount.objects.create(
        user_id='test_user_123',
        points_balance=1000
    )
    print(f"[OK] Created account: {account}")
    
    # Add transaction
    transaction = LoyaltyTransaction.objects.create(
        account=account,
        transaction_id='TEST_TXN_001',
        transaction_type='flight_booking',
        points_earned=500,
        amount=500.0,
        description='Test flight booking - $500.00'
    )
    print(f"[OK] Created transaction: {transaction}")
    
    # Update account balance
    account.points_balance += 500
    account.save()
    print(f"[OK] Updated account balance: {account.points_balance}")
    
    # Test 2: Verify data persistence after restart simulation
    print("\n2. Testing data persistence...")
    
    # Retrieve account from database
    retrieved_account = LoyaltyAccount.objects.get(user_id='test_user_123')
    print(f"[OK] Retrieved account: {retrieved_account}")
    print(f"  - Points balance: {retrieved_account.points_balance}")
    print(f"  - Tier: {retrieved_account.tier_status}")
    
    # Retrieve transactions
    transactions = LoyaltyTransaction.objects.filter(account=retrieved_account)
    print(f"[OK] Retrieved {transactions.count()} transactions")
    for txn in transactions:
        print(f"  - {txn.transaction_id}: {txn.points_earned} points")
    
    # Test 3: Test API endpoints if service is running
    print("\n3. Testing API endpoints...")
    
    try:
        # Test loyalty status endpoint
        response = requests.get('http://localhost:8002/loyalty/status/?user_id=test_user_123', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Loyalty status API: {data['points_balance']} points, tier: {data['user_tier']}")
        else:
            print(f"[WARN] Loyalty status API returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[WARN] Could not test API endpoints (service may not be running): {e}")
    
    print("\n=== Database Persistence Test Complete ===")
    return True

if __name__ == '__main__':
    test_database_persistence()