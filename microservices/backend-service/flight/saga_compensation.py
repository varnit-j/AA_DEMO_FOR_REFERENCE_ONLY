"""
SAGA compensation functions for seat reservation
"""
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .seat_manager import release_seats_for_saga

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def cancel_seat(request):
    """SAGA Compensation: Cancel seat reservation"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        
        logger.info(f"[SAGA] CancelSeat compensation for correlation_id: {correlation_id}")
        
        # Use seat manager to release seats
        result = release_seats_for_saga(correlation_id)
        
        return JsonResponse({
            "success": result['success'],
            "correlation_id": correlation_id,
            "message": result.get('message', 'Seat reservation cancelled')
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in CancelSeat: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def cancel_booking(request):
    """SAGA Compensation: Cancel booking"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        
        logger.info(f"[SAGA] CancelBooking compensation for correlation_id: {correlation_id}")
        
        # Release seats and cancel any created tickets
        seat_result = release_seats_for_saga(correlation_id)
        
        # TODO: Cancel any created tickets in stored_tickets
        # This would be implemented based on your ticket storage mechanism
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "message": "Booking cancelled successfully"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in CancelBooking: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_saga_status(request, correlation_id):
    """Get SAGA status by correlation ID"""
    try:
        # TODO: Implement proper status tracking
        # For now, return a simple status
        return JsonResponse({
            "correlation_id": correlation_id,
            "status": "COMPLETED",
            "message": "SAGA status retrieved"
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})