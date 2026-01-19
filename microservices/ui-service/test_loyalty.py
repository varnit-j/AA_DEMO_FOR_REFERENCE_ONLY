#!/usr/bin/env python
"""
Test script to add loyalty points and verify the system is working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.loyalty_tracker import add_points, get_user_points, get_user_transactions

def test_loyalty_system():
    print("=== Testing Loyalty System ===")
    
    # Test user ID 1 (your user)
    user_id = 1
    
    # Add some test points
    print("\n1. Adding test points...")
    success = add_points(user_id, 170.50, "TEST_BOOKING_001")
    print(f"   Add points result: {success}")
    
    # Add another transaction
    success = add_points(user_id, 85.25, "TEST_BOOKING_002")
    print(f"   Add points result: {success}")
    
    # Get user points
    print("\n2. Getting user points...")
    user_data = get_user_points(user_id)
    print(f"   Points balance: {user_data.get('points_balance', 0)}")
    
    # Get transactions
    print("\n3. Getting transaction history...")
    transactions = get_user_transactions(user_id)
    print(f"   Number of transactions: {len(transactions)}")
    
    for i, transaction in enumerate(transactions):
        print(f"   Transaction {i+1}:")
        print(f"     Date: {transaction.get('date')}")
        print(f"     Type: {transaction.get('type')}")
        print(f"     Points: {transaction.get('points_earned', 0)}")
        print(f"     Amount: ${transaction.get('amount', 0)}")
        print(f"     ID: {transaction.get('transaction_id')}")
        print()

if __name__ == "__main__":
    test_loyalty_system()