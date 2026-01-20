"""
SAGA Compensation for Payment Service - Complete CancelPayment
"""
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .saga_views import saga_payment_authorizations

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def cancel_payment_complete(request):
    """Complete the cancel payment compensation method"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        
        logger.info(f"[SAGA] CancelPayment compensation for correlation_id: {correlation_id}")
        
        # Check if we have an authorization record
        if correlation_id not in saga_payment_authorizations:
            logger.warning(f"[SAGA] No payment authorization found for {correlation_id}")
            return JsonResponse({
                "success": True,  # Return success even if no record found
                "message": "No payment authorization to cancel",
                "correlation_id": correlation_id
            })
        
        auth_record = saga_payment_authorizations[correlation_id]
        authorization_id = auth_record['authorization_id']
        amount = auth_record['amount']
        
        logger.info(f"[SAGA] Cancelling payment authorization {authorization_id} for ${amount}")
        
        # Mock payment cancellation
        # In real implementation, this would call payment gateway to void/cancel authorization
        
        # Update authorization record
        saga_payment_authorizations[correlation_id]['status'] = 'CANCELLED'
        saga_payment_authorizations[correlation_id]['cancelled_at'] = '2026-01-19T12:29:00Z'
        
        logger.info(f"[SAGA] Payment authorization cancelled successfully")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "authorization_id": authorization_id,
            "amount": amount,
            "status": "CANCELLED",
            "message": "Payment authorization cancelled successfully"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in CancelPayment: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })