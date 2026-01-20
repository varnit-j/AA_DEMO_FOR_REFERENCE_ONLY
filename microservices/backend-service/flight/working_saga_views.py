
"""
Working SAGA Views with real seat reservation
"""
import logging
import json
import uuid
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .seat_manager import reserve_seats_for_saga, release_seats_for_saga

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def start_booking_saga(request):
    """Start complete SAGA booking process"""
    try:
        data = json.loads(request.body)
        correlation_id = str(uuid.uuid4())
        
        logger.info(f"[SAGA] Starting booking with ID: {correlation_id}")
        
        # Step 1: Reserve Seats
        seat_result = reserve_seats_for_saga(
            correlation_id=correlation_id,
            flight_id=data['flight_id'],
            passenger_count=len(data['passengers']),
            seat_class=data.get('seat_class', 'economy'),
            user_id=data.get('user_id')
        )
        
        if not seat_result.get('success'):
            return JsonResponse({'success': False, 'error': 'Seat reservation failed'})
        
        # Step 2: Authorize Payment
        payment_url = 'http://localhost:8003/api/saga/authorize-payment/'
        payment_data = {'correlation_id': correlation_id, 'booking_data': data}
        payment_response = requests.post(payment_url, json=payment_data, timeout=10)
        
        if payment_response.status_code != 200 or not payment_response.json().get('success'):
            release_seats_for_saga(correlation_id)
            return JsonResponse({'success': False, 'error': 'Payment authorization failed'})
        
        # Step 3: Award Miles
        loyalty_url = 'http://localhost:8002/api/saga/award-miles/'
        loyalty_data = {'correlation_id': correlation_id, 'booking_data': data}
        loyalty_response = requests.post(loyalty_url, json=loyalty_data, timeout=10)
        
        if loyalty_response.status_code != 200 or not loyalty_response.json().get('success'):
            # Compensate: Cancel payment and release seats
            cancel_payment_url = 'http://localhost:8003/api/saga/cancel-payment/'
            requests.post(cancel_payment_url, json={'correlation_id': correlation_id}, timeout=5)
            release_seats_for_saga(correlation_id)
            return JsonResponse({'success': False, 'error': 'Miles award failed'})
        
        # Success - Generate booking reference
        booking_ref = f"SAGA{correlation_id[:8].upper()}"
        
        return JsonResponse({
            'success': True,
            'correlation_id': correlation_id,
            'booking_reference': booking_ref,
            'seats_reserved': seat_result.get('seats_reserved'),
            'seat_numbers': seat_result.get('seat_numbers'),
            'message': 'SAGA booking completed successfully'
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def reserve_seat(request):
    """SAGA Step 1: Reserve seat with real allocation"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        
        result = reserve_seats_for_saga(
            correlation_id=correlation