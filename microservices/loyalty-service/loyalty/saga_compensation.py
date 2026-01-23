"""
SAGA Compensation for Loyalty Service - ReverseMiles
"""
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import LoyaltyAccount, LoyaltyTransaction, SagaMilesAward
from django.utils import timezone

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def reverse_miles(request):
    """SAGA Compensation: Reverse miles awarded during booking"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        
        logger.info(f"[SAGA] ReverseMiles compensation for correlation_id: {correlation_id}")
        
        # Check if we have a SAGA award record for this correlation_id
        try:
            saga_award = SagaMilesAward.objects.get(correlation_id=correlation_id, status='AWARDED')
        except SagaMilesAward.DoesNotExist:
            logger.warning(f"[SAGA] No miles award record found for {correlation_id}")
            return JsonResponse({
                "success": True,  # Return success even if no record found
                "message": "No miles to reverse",
                "correlation_id": correlation_id
            })
        
        account = saga_award.account
        user_id = account.user_id
        miles_to_reverse = saga_award.miles_awarded
        
        logger.info(f"[SAGA] Reversing {miles_to_reverse} miles for user {user_id}")
        
        # Check current balance
        current_balance = account.points_balance
        
        if current_balance < miles_to_reverse:
            logger.warning(f"[SAGA] Insufficient miles to reverse. Current: {current_balance}, Need: {miles_to_reverse}")
            # Reverse what we can
            miles_to_reverse = current_balance
        
        # Reverse the miles
        account.points_balance -= miles_to_reverse
        account.save()  # This will also update the tier
        
        # Create compensation transaction record with enhanced identification
        LoyaltyTransaction.objects.create(
            account=account,
            transaction_id=f"COMP-{correlation_id[:8]}",
            transaction_type='adjustment',
            points_redeemed=miles_to_reverse,
            description=f'SAGA Compensation - Reversed {miles_to_reverse} miles'
        )
        
        # Update SAGA award record
        saga_award.status = 'REVERSED'
        saga_award.reversed_at = timezone.now()
        saga_award.save()
        
        logger.info(f"[SAGA] Miles reversed successfully. User {user_id}: {current_balance} -> {account.points_balance}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "miles_reversed": miles_to_reverse,
            "previous_balance": current_balance,
            "new_balance": account.points_balance
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ReverseMiles: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })