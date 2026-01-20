"""
Loyalty points tracker for microservices architecture
This module only interfaces with the loyalty service - no local storage
"""
import requests
from datetime import datetime

LOYALTY_SERVICE_URL = 'http://localhost:8002'

def call_loyalty_service(endpoint, method='GET', data=None):
    """Make API call to loyalty service"""
    try:
        url = f"{LOYALTY_SERVICE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] Loyalty service returned status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to loyalty service: {e}")
        return None

def get_user_points(user_id):
    """Get user's current points balance from loyalty service"""
    try:
        result = call_loyalty_service(f'/loyalty/status/?user_id={user_id}')
        if result:
            return {
                'points_balance': result.get('points_balance', 0),
                'user_tier': result.get('user_tier', 'Member'),
                'transactions': []  # Transactions fetched separately if needed
            }
        else:
            print(f"[ERROR] Failed to get user points from loyalty service")
            return {
                'points_balance': 0,
                'user_tier': 'Member',
                'transactions': []
            }
    except Exception as e:
        print(f"[ERROR] Error getting user points: {e}")
        return {
            'points_balance': 0,
            'user_tier': 'Member', 
            'transactions': []
        }

def get_user_transactions(user_id):
    """Get user's transaction history from loyalty service"""
    try:
        print(f"[DEBUG] TRANSACTION HISTORY - Requesting transactions for user_id: {user_id}")
        
        # Try the correct API endpoint first
        result = call_loyalty_service(f'/api/loyalty/history/{user_id}/')
        if result:
            print(f"[DEBUG] TRANSACTION HISTORY - Successfully retrieved {len(result.get('transactions', []))} transactions")
            print(f"[DEBUG] TRANSACTION HISTORY - Raw response: {result}")
            return result.get('transactions', [])
        else:
            print(f"[ERROR] TRANSACTION HISTORY - Failed to get user transactions from loyalty service")
            print(f"[DEBUG] TRANSACTION HISTORY - Trying alternative endpoint...")
            
            # Fallback to alternative endpoint
            result = call_loyalty_service(f'/loyalty/transactions/{user_id}/')
            if result:
                print(f"[DEBUG] TRANSACTION HISTORY - Alternative endpoint worked, got {len(result.get('transactions', []))} transactions")
                return result.get('transactions', [])
            else:
                print(f"[ERROR] TRANSACTION HISTORY - Both endpoints failed")
                return []
    except Exception as e:
        print(f"[ERROR] TRANSACTION HISTORY - Error getting user transactions: {e}")
        return []

# Legacy functions for backward compatibility - these should not be used in SAGA flow
def add_points(user_id, usd_amount, transaction_id):
    """Legacy function - points should be added via SAGA orchestration"""
    print(f"[WARNING] add_points() called directly - this should be handled by SAGA orchestration")
    return True  # Return success to not break existing flow

def redeem_points(user_id, points_to_redeem, transaction_id):
    """Legacy function - points should be redeemed via SAGA orchestration"""
    print(f"[WARNING] redeem_points() called directly - this should be handled by SAGA orchestration")
    return True  # Return success to not break existing flow

def load_loyalty_data():
    """Deprecated - no local storage in microservices"""
    return {}

def save_loyalty_data(data):
    """Deprecated - no local storage in microservices"""
    pass