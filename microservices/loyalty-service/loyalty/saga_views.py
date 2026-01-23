
"""
SAGA Views for Loyalty Service
Handles AwardMiles and ReverseMiles operations with enhanced logging
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

        logger.info(f"[SAGA LOYALTY] 📝 Logging detailed transaction for loyalty point history.")
        
        logger.info(f"[SAGA LOYALTY] 🎯 AwardMiles step initiated for correlation_id: {correlation_id}")
        logger.info(f"[SAGA LOYALTY] 📊 Booking data received: flight_id={booking_data.get('flight_id')}, user_id={booking_data.get('user_id')}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA LOYALTY] ❌ Simulated failure in AwardMiles for {correlation_id}")
            logger.error(f"[SAGA LOYALTY] 🔄 This will trigger compensation for previous steps (seat reservation & payment)")
            return JsonResponse({
                "success": False,
                "error": "Simulated miles award failure - loyalty service temporarily unavailable"
            })
        
        # Extract booking information with detailed logging
        user_id = str(booking_data.get('user_id', '1'))
        flight_fare = booking_data.get('flight_fare', 0)
        
        logger.info(f"[SAGA LOYALTY] 💰 Processing miles award for user {user_id}")
        logger.info(f"[SAGA LOYALTY] 💵 Flight fare from booking_data: ${flight_fare}")
        
        if not flight_fare:
            # Try to get fare from flight data
            flight_data = booking_data.get('flight', {})
            flight_fare = flight_data.get('economy_fare', 500)  # Default fare
            logger.warning(f"[SAGA LOYALTY] ⚠️ Using fallback fare from flight data: ${flight_fare}")
        
        # Calculate miles: 1 dollar = 1 mile
        miles_to_award = int(float(flight_fare))
        
        logger.info(f"[SAGA LOYALTY] 🏆 Calculating miles award: ${flight_fare} = {miles_to_award} miles (1:1 ratio)")
        
        # Get or create loyalty account with detailed logging
        account, created = LoyaltyAccount.objects.get_or_create(user_id=user_id)
        if created:
            logger.info(f"[SAGA LOYALTY] 🆕 Created new loyalty account for user {user_id}")
        else:
            logger.info(f"[SAGA LOYALTY] 📋 Found existing loyalty account for user {user_id}")
        
        original_balance = account.points_balance
        original_tier = account.tier_status
        logger.info(f"[SAGA LOYALTY] 📊 Current account status: {original_balance} miles, tier: {original_tier}")
        
        # Add miles to user balance
        account.points_balance += miles_to_award
        account.save()  # This will also update the tier
        
        new_tier = account.tier_status
        tier_changed = original_tier != new_tier
        
        if tier_changed:
            logger.info(f"[SAGA LOYALTY] 🎉 TIER UPGRADE! User {user_id}: {original_tier} -> {new_tier}")
        
        # Create SAGA award record for compensation tracking
        saga_award = SagaMilesAward.objects.create(
            correlation_id=correlation_id,
            account=account,
            miles_awarded=miles_to_award,
            original_balance=original_balance,
            new_balance=account.points_balance,
            status='AWARDED'
        )
        logger.info(f"[SAGA LOYALTY] 💾 Created SAGA award record: {saga_award.id}")
        
        # Create transaction record
        transaction = LoyaltyTransaction.objects.create(
            account=account,
            transaction_id=f"SAGA-{correlation_id[:8]}",
            transaction_type='flight_booking',
            points_earned=miles_to_award,
            amount=flight_fare,
            description=f'✈️ SAGA Flight booking - ${flight_fare:.2f} -> {miles_to_award} miles'
        )
        logger.info(f"[SAGA LOYALTY] 📝 Created transaction record: {transaction.transaction_id}")
        
        logger.info(f"[SAGA LOYALTY] ✅ Miles awarded successfully! User {user_id}: {original_balance} -> {account.points_balance} miles")
        
        # Log detailed transaction for loyalty point history
        logger.info(f"[SAGA LOYALTY] 📝 Transaction logged: {transaction.transaction_id} - {miles_to_award} miles awarded for booking.")
        
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

@csrf_exempt
@require_http_methods(["POST"])
def reverse_miles(request):
    """SAGA Compensation: Reverse miles award"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        compensation_reason = data.get('compensation_reason', 'SAGA compensation')

        # DIAGNOSTIC: Enhanced logging for compensation debugging
        logger.info(f"[COMPENSATION_DEBUG] ===== LOYALTY COMPENSATION RECEIVED =====")
        logger.info(f"[COMPENSATION_DEBUG] Request method: {request.method}")
        logger.info(f"[COMPENSATION_DEBUG] Request path: {request.path}")
        logger.info(f"[COMPENSATION_DEBUG] Request body: {request.body}")
        logger.info(f"[COMPENSATION_DEBUG] Parsed data: {data}")
        logger.info(f"[COMPENSATION_DEBUG] Correlation ID: {correlation_id}")
        logger.info(f"[COMPENSATION_DEBUG] Compensation reason: {compensation_reason}")

        logger.info(f"[SAGA COMPENSATION] 📝 Logging detailed transaction for reversed loyalty points.")
        
        logger.error(f"[SAGA COMPENSATION] 🚨 LOYALTY COMPENSATION CALLED for correlation_id: {correlation_id}")
        logger.error(f"[SAGA COMPENSATION] 🚨 This confirms loyalty compensation is being triggered!")
        logger.info(f"[SAGA COMPENSATION] 🔄 ReverseMiles compensation initiated for correlation_id: {correlation_id}")
        logger.info(f"[SAGA COMPENSATION] 📋 Compensation reason: {compensation_reason}")
        
        # Find the original SAGA award
        try:
            saga_award = SagaMilesAward.objects.get(correlation_id=correlation_id, status='AWARDED')
            logger.info(f"[SAGA COMPENSATION] 🎯 Found SAGA award record: {saga_award.id}")
        except SagaMilesAward.DoesNotExist:
            logger.warning(f"[SAGA COMPENSATION] ⚠️ No SAGA award found for {correlation_id}")
            logger.info(f"[SAGA COMPENSATION] ✅ No compensation needed - no miles were awarded")
            return JsonResponse({
                "success": True,  # Return success even if no award found
                "correlation_id": correlation_id,
                "message": "No miles award found to reverse - compensation complete"
            })
        
        # Get the loyalty account
        account = saga_award.account
        user_id = account.user_id
        miles_to_reverse = saga_award.miles_awarded
        
        logger.info(f"[SAGA COMPENSATION] 💰 Reversing {miles_to_reverse} miles from user {user_id}")
        logger.info(f"[SAGA COMPENSATION] 📊 Original award: {saga_award.original_balance} -> {saga_award.new_balance} miles")
        
        # Store original balance before reversal
        original_balance = account.points_balance
        original_tier = account.tier_status
        
        logger.info(f"[SAGA COMPENSATION] 📊 Account before reversal: {original_balance} miles, tier: {original_tier}")
        
        # Reverse the miles
        account.points_balance -= miles_to_reverse
        if account.points_balance < 0:
            logger.warning(f"[SAGA COMPENSATION] ⚠️ Preventing negative balance: setting to 0")
            account.points_balance = 0  # Prevent negative balance
        account.save()  # This will also update the tier
        
        new_tier = account.tier_status
        tier_changed = original_tier != new_tier
        
        if tier_changed:
            logger.info(f"[SAGA COMPENSATION] 📉 TIER DOWNGRADE due to compensation: {original_tier} -> {new_tier}")
        
        # Update SAGA award status
        saga_award.status = 'REVERSED'
        saga_award.reversed_at = timezone.now()
        saga_award.save()
        logger.info(f"[SAGA COMPENSATION] 💾 Updated SAGA award status to REVERSED")
        
        # Create compensation transaction record with enhanced identification
        comp_transaction = LoyaltyTransaction.objects.create(
            account=account,
            transaction_id=f"COMP-{correlation_id[:8]}",
            transaction_type='adjustment',
            points_redeemed=miles_to_reverse,
            amount=0.0,
            description=f'SAGA Compensation: {compensation_reason} - Reversed {miles_to_reverse} miles'
        )
        logger.info(f"[SAGA COMPENSATION] 📝 Created compensation transaction: {comp_transaction.transaction_id}")
        
        # DIAGNOSTIC: Log compensation transaction details for dashboard debugging
        logger.info(f"[DASHBOARD_DEBUG] Compensation transaction created:")
        logger.info(f"[DASHBOARD_DEBUG] - Transaction ID: {comp_transaction.transaction_id}")
        logger.info(f"[DASHBOARD_DEBUG] - Transaction Type: {comp_transaction.transaction_type}")
        logger.info(f"[DASHBOARD_DEBUG] - Points Redeemed: {comp_transaction.points_redeemed}")
        logger.info(f"[DASHBOARD_DEBUG] - Description: {comp_transaction.description}")
        logger.info(f"[DASHBOARD_DEBUG] - Account User ID: {account.user_id}")
        logger.info(f"[DASHBOARD_DEBUG] - Created At: {comp_transaction.created_at}")
        
        logger.info(f"[SAGA COMPENSATION] ✅ Miles reversal completed! User {user_id}: {original_balance} -> {account.points_balance} miles")
        
        # Log detailed transaction for loyalty point history
        logger.info(f"[SAGA COMPENSATION] 📝 Compensation transaction logged: {comp_transaction.transaction_id} - {miles_to_reverse} miles reversed.")
        logger.info(f"[SAGA COMPENSATION] 🎯 Loyalty service compensation successful for correlation_id: {correlation_id}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "miles_reversed": miles_to_reverse,
            "original_balance": original_balance,
            "new_balance": account.points_balance,
            "message": f"Successfully reversed {miles_to_reverse} miles due to SAGA compensation"
        })
        
    except Exception as e:
        logger.error(f"[SAGA COMPENSATION] ❌ Error in ReverseMiles: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })