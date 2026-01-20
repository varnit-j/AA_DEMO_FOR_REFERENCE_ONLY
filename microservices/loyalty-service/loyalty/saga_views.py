
"""
SAGA Views for Loyalty Service
Handles AwardMiles and ReverseMiles operations
"""
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# Import database models
from .models import LoyaltyAccount, LoyaltyTransaction, SagaMilesAward
from django.utils import timezone

@csrf_exempt
@require_http_methods(["POST"])
def award_miles(request):
    """SAGA Step 3: Award miles for successful booking"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        simulate_failure = data.get('simulate_failure', False)
        
        logger.info(f"[SAGA] AwardMiles step for correlation_id: {correlation_id}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA] Simulated failure in AwardMiles for {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": "Simulated miles award failure"
            })
        
        # Extract booking information
        user_id = str(booking_data.get('user_id', '1'))
        flight_fare = booking_data.get('flight_fare', 0)
        
        if not flight_fare:
            # Try to get fare from flight data
            flight_data = booking_data.get('flight', {})
            flight_fare = flight_data.get('economy_fare', 500)  # Default fare
        
        # Calculate miles: 1 dollar = 1 mile
        miles_to_award = int(float(flight_fare))
        
        logger.info(f"[SAGA] Awarding {miles_to_award} miles to user {user_id}")
        
        # Get or create loyalty account
        account, created = LoyaltyAccount.objects.get_or_create(user_id=user_id)
        if created:
            logger.info(f"[SAGA] Created new loyalty account for user {user_id}")
        
        original_balance = account.points_balance
        
        # Add miles to user balance
        account.points_balance += miles_to_award
        account.save()  # This will also update the tier
        
        # Create SAGA award record for compensation tracking
        saga_award = SagaMilesAward.objects.create(
            correlation_id=correlation_id,
            account=account,
            miles_awarded=miles_to_award,
            original_balance=original_balance,
            new_balance=account.points_balance,
            status='AWARDED'
        )
        
        # Create transaction record
        LoyaltyTransaction.objects.create(
            account=account,
            transaction_id=f"SAGA-{correlation_id[:8]}",
            transaction_type='flight_booking',
            points_earned=miles_to_award,
            amount=flight_fare,
            description=f'SAGA Flight booking - ${flight_fare:.2f}'
        )
        
        logger.info(f"[SAGA] Miles awarded successfully. User {user_id}: {original_balance} -> {account.points_balance}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "miles_awarded": miles_to_award,
            "original_balance": original_balance,
            "new_balance": account.points_balance
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in AwardMiles: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })