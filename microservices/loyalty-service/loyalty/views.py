from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Simple in-memory storage for demo purposes
# In production, this would be a database
user_points = {}
transaction_history = {}

def loyalty_status(request):
    """Basic loyalty status endpoint for AAdvantage dashboard"""
    user_id = request.GET.get('user_id', '1')  # Default to user 1 for demo
    
    print(f"[DEBUG] Loyalty status request for user_id: {user_id}")
    print(f"[DEBUG] Current user_points storage: {user_points}")
    
    # Get current points balance
    current_points = user_points.get(user_id, 0)
    print(f"[DEBUG] Points for user {user_id}: {current_points}")
    
    # Calculate tier based on points
    if current_points >= 125000:
        tier = 'ConciergeKey'
        miles_to_next = 0
    elif current_points >= 100000:
        tier = 'Executive Platinum'
        miles_to_next = 125000 - current_points
    elif current_points >= 75000:
        tier = 'Platinum Pro'
        miles_to_next = 100000 - current_points
    elif current_points >= 50000:
        tier = 'Platinum'
        miles_to_next = 75000 - current_points
    elif current_points >= 25000:
        tier = 'Gold'
        miles_to_next = 50000 - current_points
    else:
        tier = 'Regular'
        miles_to_next = 25000 - current_points
    
    return JsonResponse({
        'status': 'active',
        'service': 'loyalty-service',
        'message': 'AAdvantage loyalty program is active',
        'user_tier': tier,
        'points_balance': current_points,
        'miles_to_next_tier': miles_to_next,
        'benefits': [
            'Priority boarding',
            'Free checked bags',
            'Lounge access',
            'Upgrade eligibility'
        ]
    })

@csrf_exempt
@require_http_methods(["POST"])
def add_transaction_points(request):
    """Add points for a transaction (2% of transaction amount)"""
    try:
        data = json.loads(request.body)
        user_id = str(data.get('user_id', '1'))
        transaction_amount = float(data.get('amount', 0))
        transaction_id = data.get('transaction_id', '')
        
        print(f"[DEBUG] Received transaction data: {data}")
        print(f"[DEBUG] Transaction amount: ${transaction_amount}")
        
        # Calculate points: 1 dollar = 1 point (as requested)
        points_earned = int(transaction_amount)
        print(f"[DEBUG] Points calculation: ${transaction_amount} = {points_earned} points (1:1 ratio)")
        
        # Add points to user balance
        if user_id not in user_points:
            user_points[user_id] = 0
        user_points[user_id] += points_earned
        
        # Store transaction history
        if user_id not in transaction_history:
            transaction_history[user_id] = []
        
        transaction_history[user_id].append({
            'transaction_id': transaction_id,
            'amount': transaction_amount,
            'points_earned': points_earned,
            'date': '2026-01-15',  # Simplified for demo
            'type': 'flight_booking'
        })
        
        print(f"[DEBUG] Added {points_earned} points for user {user_id}, transaction ${transaction_amount}")
        
        return JsonResponse({
            'success': True,
            'points_earned': points_earned,
            'total_points': user_points[user_id],
            'message': f'Earned {points_earned} points from transaction'
        })
        
    except Exception as e:
        print(f"[ERROR] Add transaction points error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_transaction_history(request, user_id):
    """Get transaction history for a user"""
    try:
        user_transactions = transaction_history.get(str(user_id), [])
        return JsonResponse({
            'user_id': user_id,
            'transactions': user_transactions,
            'total_transactions': len(user_transactions)
        })
    except Exception as e:
        print(f"[ERROR] Get transaction history error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def redeem_points(request):
    """Redeem points for payment (deduct from user balance)"""
    try:
        data = json.loads(request.body)
        user_id = str(data.get('user_id', '1'))
        points_to_redeem = int(data.get('points_to_redeem', 0))
        transaction_id = data.get('transaction_id', '')
        
        print(f"[DEBUG] Points redemption request: {data}")
        
        # Check if user has enough points
        current_points = user_points.get(user_id, 0)
        if points_to_redeem > current_points:
            return JsonResponse({
                'error': f'Insufficient points. Available: {current_points}, Requested: {points_to_redeem}'
            }, status=400)
        
        # Deduct points from user balance
        user_points[user_id] -= points_to_redeem
        points_value = points_to_redeem * 0.01  # 1 point = $0.01
        
        # Store redemption transaction
        if user_id not in transaction_history:
            transaction_history[user_id] = []
        
        transaction_history[user_id].append({
            'transaction_id': transaction_id,
            'points_redeemed': points_to_redeem,
            'points_value': points_value,
            'date': '2026-01-15',  # Simplified for demo
            'type': 'miles_redemption'
        })
        
        print(f"[DEBUG] Redeemed {points_to_redeem} points (${points_value:.2f}) for user {user_id}")
        
        return JsonResponse({
            'success': True,
            'points_redeemed': points_to_redeem,
            'points_value': points_value,
            'remaining_points': user_points[user_id],
            'message': f'Redeemed {points_to_redeem} points worth ${points_value:.2f}'
        })
        
    except Exception as e:
        print(f"[ERROR] Points redemption error: {e}")
        return JsonResponse({'error': str(e)}, status=500)