"""
Simple local loyalty points tracker
Since the loyalty service is not running, we'll track points locally
"""
import json
import os
from datetime import datetime

LOYALTY_FILE = 'local_loyalty_points.json'

def load_loyalty_data():
    """Load loyalty data from local file"""
    if os.path.exists(LOYALTY_FILE):
        try:
            with open(LOYALTY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_loyalty_data(data):
    """Save loyalty data to local file"""
    try:
        with open(LOYALTY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[DEBUG] Error saving loyalty data: {e}")

def add_points(user_id, usd_amount, transaction_id):
    """Add points: 1 USD = 1 point"""
    try:
        data = load_loyalty_data()
        user_key = str(user_id)
        
        if user_key not in data:
            data[user_key] = {
                'points_balance': 0,
                'transactions': []
            }
        
        points_to_add = int(float(usd_amount))  # 1 USD = 1 point
        data[user_key]['points_balance'] += points_to_add
        
        # Add transaction record in format expected by template
        transaction = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'type': 'flight_booking',
            'points_earned': points_to_add,
            'amount': float(usd_amount),
            'transaction_id': transaction_id,
            'description': f'Flight booking - ${usd_amount:.2f}'
        }
        data[user_key]['transactions'].append(transaction)
        
        save_loyalty_data(data)
        print(f"[DEBUG] Added {points_to_add} points for user {user_id} (${usd_amount})")
        return True
    except Exception as e:
        print(f"[DEBUG] Error adding points: {e}")
        return False

def redeem_points(user_id, points_to_redeem, transaction_id):
    """Redeem points"""
    try:
        data = load_loyalty_data()
        user_key = str(user_id)
        
        if user_key not in data:
            return False
        
        if data[user_key]['points_balance'] < points_to_redeem:
            return False
        
        data[user_key]['points_balance'] -= points_to_redeem
        
        # Add transaction record in format expected by template
        transaction = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'type': 'miles_redemption',
            'points_redeemed': points_to_redeem,
            'points_value': points_to_redeem * 0.01,  # 1 point = $0.01
            'transaction_id': transaction_id,
            'description': f'Points redemption - {points_to_redeem} points'
        }
        data[user_key]['transactions'].append(transaction)
        
        save_loyalty_data(data)
        print(f"[DEBUG] Redeemed {points_to_redeem} points for user {user_id}")
        return True
    except Exception as e:
        print(f"[DEBUG] Error redeeming points: {e}")
        return False

def get_user_points(user_id):
    """Get user's current points balance"""
    try:
        data = load_loyalty_data()
        user_key = str(user_id)
        
        if user_key not in data:
            return {
                'points_balance': 0,
                'transactions': []
            }
        
        return data[user_key]
    except Exception as e:
        print(f"[DEBUG] Error getting user points: {e}")
        return {
            'points_balance': 0,
            'transactions': []
        }

def get_user_transactions(user_id):
    """Get user's transaction history"""
    try:
        data = load_loyalty_data()
        user_key = str(user_id)
        
        if user_key not in data:
            return []
        
        return data[user_key].get('transactions', [])
    except Exception as e:
        print(f"[DEBUG] Error getting user transactions: {e}")
        return []