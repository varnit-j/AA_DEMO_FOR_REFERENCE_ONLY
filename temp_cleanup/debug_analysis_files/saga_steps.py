
"""
Individual SAGA step implementations with real seat reservation
"""
import logging
import json
import secrets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Flight, Ticket, Passenger
from .seat_manager import reserve_seats_for_saga, release_seats_for_saga, confirm_seat_reservation, SeatAllocationError
from .simple_views import stored_tickets

logger = logging.getLogger(__name__)

def generate_ref_no():
    """Generate a unique reference number for tickets"""
    return secrets.token_hex(3).upper()

@csrf_exempt
@require_http_methods(["POST"])
def reserve_seat(request):
    """SAGA Step 1: Reserve seat for booking with real seat allocation"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        simulate_failure = data.get('simulate_failure', False)
        
        logger.info(f"[SAGA] ReserveSeat step for correlation_id: {correlation_id}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA] Simulated failure in ReserveSeat for {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": "Simulated seat reservation failure"
            })
        
        # Extract booking information
        flight_id = booking_data.get('flight_id')
        passengers_data = booking_data.get('passengers', [])
        user_id = booking_data.get('user_id')
        seat_class = booking_data.get('seat_class', 'economy')
        
        if not flight_id or not passengers_data:
            return JsonResponse({
                "success": False,
                "error": "Missing flight_id or passengers data"
            })
        
        # Use seat manager to reserve actual seats
        try:
            result = reserve_seats_for_saga(
                correlation_id=correlation_id,
                flight_id=flight_id,
                passenger_count=len(passengers_data),
                seat_class=seat_class,
                user_id=user_id
            )
            
            logger.info(f"[SAGA] Seat reservation successful: {result}")
            
            return JsonResponse({
                "success": True,
                "correlation_id": correlation_id,
                "reservation_id": correlation_id,
                "seats_reserved": result['seats_reserved'],
                "seat_numbers": result['seat_numbers'],
                "flight_id": flight_id
            })
            
        except SeatAllocationError as e:
            logger.error(f"[SAGA] Seat allocation failed: {e}")
            return JsonResponse({
                "success": False,
                "error": str(e)
            })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ReserveSeat: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def confirm_booking(request):
    """SAGA Step 4: Confirm booking and create ticket"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        
        logger.info(f"[SAGA] ConfirmBooking step for correlation_id: {correlation_id}")
        
        # Confirm seat reservation
        confirm_result = confirm_seat_reservation(correlation_id)
        if not confirm_result['success']:
            return JsonResponse({
                "success": False