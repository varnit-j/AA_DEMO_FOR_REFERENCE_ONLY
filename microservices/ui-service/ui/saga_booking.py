"""
SAGA booking integration for UI service
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def call_saga_booking_api(booking_data):
    """Call the SAGA booking API"""
    try:
        backend_url = settings.BACKEND_SERVICE_URL
        saga_url = f"{backend_url}/api/saga/start-booking/"
        
        logger.info(f"[SAGA] Calling SAGA booking API: {saga_url}")
        logger.info(f"[SAGA] Booking data: {booking_data}")
        
        response = requests.post(saga_url, json=booking_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"[SAGA] SAGA booking successful: {result}")
            return result
        else:
            logger.error(f"[SAGA] SAGA booking failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"[SAGA] Error calling SAGA booking API: {e}")
        return None

def book_flight_with_saga(request, booking_data):
    """Book flight using SAGA pattern"""
    try:
        logger.info(f"[SAGA] Starting SAGA booking for user {request.user.id}")
        
        # Prepare SAGA booking data
        saga_booking_data = {
            'flight_id': booking_data['flight_id'],
            'user_id': request.user.id,
            'passengers': booking_data['passengers'],
            'contact_info': booking_data['contact_info'],
            'seat_class': booking_data.get('seat_class', 'economy')
        }
        
        # Call SAGA booking API
        result = call_saga_booking_api(saga_booking_data)
        
        if result and result.get('success'):
            return {
                'success': True,
                'booking_reference': result.get('booking_reference'),
                'correlation_id': result.get('correlation_id'),
                'seats_reserved': result.get('seats_reserved'),
                'seat_numbers': result.get('seat_numbers'),
                'message': 'SAGA booking completed successfully',
                'booking_type': 'SAGA'
            }
        else:
            error_msg = result.get('error', 'SAGA booking failed') if result else 'SAGA service unavailable'
            return {
                'success': False,
                'error': error_msg,
                'booking_type': 'SAGA'
            }
            
    except Exception as e:
        logger.error(f"[SAGA] Error in SAGA booking: {e}")
        return {
            'success': False,
            'error': str(e),
            'booking_type': 'SAGA'
        }