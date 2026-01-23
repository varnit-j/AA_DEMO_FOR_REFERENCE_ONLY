
"""
Simple SAGA Orchestrator for Flight Booking
Coordinates: ReserveSeat → AuthorizePayment → AwardMiles → ConfirmBooking
"""
import logging
import uuid
import requests
from typing import Dict, Any
from .seat_manager import reserve_seats_for_saga, release_seats_for_saga, confirm_seat_reservation

logger = logging.getLogger(__name__)

class BookingOrchestrator:
    """Simple SAGA Orchestrator for flight booking process"""
    
    def __init__(self):
        self.services = {
            'backend': 'http://localhost:8001',
            'payment': 'http://localhost:8003', 
            'loyalty': 'http://localhost:8002'
        }
    
    def start_booking_saga(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start the booking SAGA process"""
        correlation_id = str(uuid.uuid4())
        
        logger.info(f"[SAGA] Starting booking SAGA with correlation_id: {correlation_id}")
        
        try:
            # Step 1: Reserve Seat
            logger.info(f"[SAGA] Step 1: Reserving seats")
            seat_result = self._reserve_seat(correlation_id, booking_data)
            if not seat_result.get('success'):
                return {'success': False, 'error': 'Seat reservation failed', 'step': 'ReserveSeat'}
            
            # Step 2: Authorize Payment
            logger.info(f"[SAGA] Step 2: Authorizing payment")
            payment_result = self._authorize_payment(correlation_id, booking_data)
            if not payment_result.get('success'):
                # Compensate: Release seats
                self._release_seats(correlation_id)
                return {'success': False, 'error': 'Payment authorization failed', 'step': 'AuthorizePayment'}
            
            # Step 3: Award Miles
            logger.info(f"[SAGA] Step 3: Awarding miles")
            miles_result = self._award_miles(correlation_id, booking_data)
            if not miles_result.get('success'):
                # Compensate: Cancel payment and release seats
                self._cancel_payment(correlation_id, booking_data)
                self._release_seats(correlation_id)
                return {'success': False, 'error': 'Miles award failed', 'step': 'AwardMiles'}
            
            # Step 4: Confirm Booking
            logger.info(f"[SAGA] Step 4: Confirming booking")
            booking_result = self._confirm_booking(correlation_id, booking_data)
            if not booking_result.get('success'):
                # Compensate: Reverse miles, cancel payment, release seats
                self._reverse_miles(correlation_id, booking_data)
                self._cancel_payment(correlation_id, booking_data)
                self._release_seats(correlation_id)
                return {'success': False, 'error': 'Booking confirmation failed', 'step': 'ConfirmBooking'}
            
            logger.info(f"[SAGA] Booking SAGA completed successfully")
            return {
                'success': True,
                'correlation_id': correlation_id,
                'booking_reference': booking_result.get('booking_reference'),
                'seats_reserved': seat_result.get('seats_reserved'),
                'seat_numbers': seat_result.get('seat_numbers'),
                'message': 'Booking completed successfully'
            }
            
        except Exception as e:
            logger.error(f"[SAGA] Error in booking SAGA: {e}")
            # Try to compensate
            try:
                self._release_seats(correlation_id)
            except:
                pass
            return {'