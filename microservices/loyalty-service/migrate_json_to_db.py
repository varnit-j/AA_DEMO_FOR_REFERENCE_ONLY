
#!/usr/bin/env python3
"""
Migration script to transfer existing JSON loyalty data to database
"""
import os
import sys
import django
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loyalty.settings')
django.setup()

from loyalty.models import LoyaltyAccount, LoyaltyTransaction

def migrate_json_data():
    """Migrate existing JSON data to database"""
    print("=== Migrating JSON Data to Database ===")
    
    # Path to the UI service JSON file
    json_file_path = '../ui-service/local_loyalty_points.json'
    
    if not os.path.exists(json_file_path):
        print(f"[INFO] No JSON file found at {json_file_path}")
        return
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        print(f"[INFO] Found data for {len(data)} users")
        
        for user_id, user_data in data.items():
            print(f"\n[INFO] Migrating user {user_id}...")
            
            # Get or create loyalty account
            account, created = LoyaltyAccount.objects.get_or_create(
                user_id=user_id,
                defaults={'points_balance': user_data.get('points_balance', 0)}
            )
            
            if not created:
                # Update existing account
                account.points_balance = user_data.get('points_balance', 0)
                account.save()
                print(f"  [OK] Updated existing account: {account.points_balance} points")
            else:
                print(f"  [OK] Created new account: {account.points_balance} points")
            
            # Migrate transactions
            transactions = user_data.get('transactions', [])
            print(f"  [INFO] Migrating {len(transactions)} transactions...")
            
            for txn in transactions:
                # Check if transaction already exists
                existing_txn = LoyaltyTransaction.objects.filter(
                    account=account,
                    transaction_id=txn.get('transaction_id', '')
                ).first()
                
                if existing_txn:
                    print(f"    [SKIP] Transaction {txn.get('transaction_id')} already exists")
                    continue
                
                # Create new transaction
                transaction_data = {
                    'account': account,
                    'transaction_id': txn.get('transaction_id', ''),
                    'transaction_type': txn.get('type', 'flight_booking'),
                    'description': txn.get('description', ''),
                }
                
                if 'points_earned' in txn:
                    transaction_data.update({
                        'points_earned': txn['points_earned'],
                        'amount': txn.get('amount', 0.0)
                    })
                elif 'points_redeemed' in txn:
                    transaction_data.update({
                        'points_redeemed': txn['points_redeemed'],
                        'points_value': txn.get('points_value', 0.0)
                    })
                
                LoyaltyTransaction.objects.create(**transaction_data)
                print(f"    [OK] Migrated transaction {txn.get('transaction_id')}")
        
        print(f"\n[SUCCESS] Migration completed successfully!")
        
        # Show summary
        total_accounts = LoyaltyAccount.objects.count()
        total_transactions = LoyaltyTransaction.objects.count()
        print(f"\n[SUMMARY]")
        print(f"  Total accounts in database: {total_accounts}")
        print(f"  Total transactions in database: {total_transactions}")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    migrate_json_data()