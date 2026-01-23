
"""
Working SAGA Orchestrator for Flight Booking
"""
import logging
import uuid
import requests
from .seat_manager import reserve_seats_for_saga, release_seats_for_saga

logger = logging.getLogger(__name__)

class BookingOrchestrator:
    def __init__(self):
        self.services = {
            'payment': 'http://localhost:8003',
            'loyalty': 'http://localhost:8002'
        }
    
    def start_booking_saga(self, booking_data):
        correlation_id = str(uuid.uuid4())
        logger.info(f"[SAGA] Starting booking with ID: {correlation_id}")
        
        try:
            # Step 1: Reserve Seats
            seat_result = reserve_seats_for_saga(
                correlation_id=correlation_id,
                flight_id=booking_data['flight_id'],
                passenger_count=len(booking_data['passengers']),
                seat_class=booking_data.get('seat_class', 'economy'),
                user_id=booking_data.get('user_id')
            )
            
            if not seat_result.get('success'):
                return {'success': False, 'error': 'Seat reservation failed'}
            
            # Step 2: Authorize Payment
            payment_result = self._call_payment_service(correlation_id, booking_data)
            if not payment_result.get('success'):
                release_seats_for_saga(correlation_id)
                return {'success': False, 'error': 'Payment failed'}
            
            # Step 3: Award Miles
            miles_result = self._call_loyalty_service(correlation_id, booking_data)
            if not miles_result.get('success'):
                self._cancel_payment(correlation_id)
                release_seats_for_saga(correlation_id)
                return {'success': False, 'error': 'Miles award failed'}
            
            # Step 4: Confirm Booking
            booking_ref = f"SAGA{correlation_id[:8].upper()}"
            
            return {
                'success': True,
                'correlation_id': correlation_id,
                'booking_reference': booking_ref,
                'seats_reserved': seat_result.get('seats_reserved'),
                'seat_numbers': seat_result.get('seat_numbers'),
                'message': 'SAGA booking completed successfully'
            }
            
        except Exception as e:
            logger.error(f"[SAGA] Error: {e}")
            try:
                release_seats_for_saga(correlation_id)
            except:
                pass
            return {'success': False, 'error': str(e)}
    
    def _call_payment_service(self, correlation_id, booking_data):
        try:
            url = f"{self.services['payment']}/api/saga/authorize-payment/"
            payload = {'correlation_id': correlation_id, 'booking_data': booking_data}
            response = requests.post(url, json=payload, timeout=10)
            return response.json() if response.status_code == 200 else {'success': False}
        except:
            return {'success': False}
    
    def _call_loyalty_service(self, correlation_id, booking_data):
        try:
            url = f"{self.services['loyalty']}/api/saga/award-miles/"
            payload = {'correlation_id': correlation_id, 'booking_data': booking_data}
            response = requests.post(url, json=payload, timeout=10)
            return