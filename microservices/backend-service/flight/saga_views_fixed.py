
"""
Fixed SAGA Views for Backend Service - Issue Resolution
Fixes the missing booking creation and miles calculation issues
"""
import logging
import json
import uuid
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Flight, Place, Week, SagaTransaction, SagaPaymentAuthorization, SagaMilesAward, SeatReservation, Ticket, Passenger
from .simple_views import stored_tickets
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def confirm_booking_fixed(request):
    """SAGA Step 4: Confirm booking and create ticket - FIXED VERSION"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        
        logger.info(f"[SAGA] ConfirmBooking step for correlation_id: {correlation_id}")
        
        # Get SAGA transaction to retrieve booking details
        try:
            saga_transaction = SagaTransaction.objects.get(correlation_id=correlation_id)
            flight = saga_transaction.flight
            user_id = saga_transaction.user_id
            booking_info = saga_transaction.booking_data
            
            # Create passengers
            passengers_list = []
            for passenger_data in booking_info.get('passengers', []):
                passenger = Passenger.objects.create(
                    first_name=passenger_data.get('first_name', ''),
                    last_name=passenger_data.get('last_name', ''),
                    gender=passenger_data.get('gender', 'male')
                )
                passengers_list.append(passenger)
            
            # Create ticket with correlation_id as booking reference
            contact_info = booking_info.get('contact_info', {})
            ticket = Ticket.objects.create(
                user_id=user_id,
                ref_no=correlation_id,  # Use correlation_id as booking reference
                flight=flight,
                flight_ddate=timezone.now().date(),  # Today's date for demo
                flight_adate=timezone.now().date(),  # Today's date for demo
                flight_fare=float(flight.economy_fare),
                other_charges=50.0,  # Standard charges
                total_fare=float(flight.economy_fare) + 50.0,
                seat_class='economy',
                mobile=contact_info.get('mobile', ''),
                email=contact_info.get('email', ''),
                status='CONFIRMED'  # SAGA booking is confirmed
            )
            
            # Add passengers to ticket
            ticket.passengers.set(passengers_list)
            ticket.save()
            
            logger.info(f"[SAGA] Ticket created successfully: {ticket.ref_no}")
            
            return JsonResponse({
                "success": True,
                "correlation_id": correlation_id,
                "booking_reference": ticket.ref_no,
                "message": "Booking confirmed and ticket created successfully"
            })
            
        except SagaTransaction.DoesNotExist:
            logger.error(f"[SAGA] SAGA transaction not found for correlation_id: {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": f"SAGA transaction not found for correlation_id: {correlation_id}"
            })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ConfirmBooking: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def