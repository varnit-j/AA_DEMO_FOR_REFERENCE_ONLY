"""
SAGA Service for Flight Booking
Integrates SAGA Orchestrator with Django models and business logic
"""

import logging
from typing import Dict, Any, Optional
from .models import Ticket, User, Flight
from .saga_orchestrator import BookingSAGAOrchestrator

logger = logging.getLogger(__name__)


class BookingSAGAService:
    """Service for managing flight booking SAGA"""
    
    def __init__(self):
        self.orchestrator = None
        
    def create_booking_saga(
        self,
        user: User,
        flight_ids: list,
        flight_dates: list,
        passenger_data: list,
        seat_class: str,
        total_fare: float,
        loyalty_points_to_use: int = 0,
        payment_method: str = 'card',
        failure_scenarios: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Create and execute a booking SAGA
        
        Args:
            user: Django User instance
            flight_ids: List of flight IDs to book
            flight_dates: List of flight dates (as strings 'dd-mm-yyyy')
            passenger_data: List of passenger dictionaries
            seat_class: Seat class (Economy, Business, First)
            total_fare: Total fare amount
            loyalty_points_to_use: Loyalty points to redeem
            payment_method: Payment method (card, counter)
            failure_scenarios: Dict specifying which steps should fail for testing
            
        Returns:
            SAGA result dictionary
        """
        try:
            # Prepare booking data
            booking_data = {
                'user_id': user.id,
                'user_email': user.email,
                'user_name': f"{user.first_name} {user.last_name}",
                'flight_ids': flight_ids,
                'flight_dates': flight_dates,
                'passengers': passenger_data,
                'seat_class': seat_class,
                'total_fare': total_fare,
                'loyalty_points_to_use': loyalty_points_to_use,
                'payment_method': payment_method,
                'booking_timestamp': str(__import__('datetime').datetime.now().isoformat())
            }
            
            logger.info(f"[BOOKING_SAGA_SERVICE] Creating booking SAGA for user {user.id}")
            logger.debug(f"[BOOKING_SAGA_SERVICE] Booking data: {booking_data}")
            
            # Create and execute orchestrator
            self.orchestrator = BookingSAGAOrchestrator()
            result = self.orchestrator.start_booking_saga(
                booking_data,
                failure_scenarios=failure_scenarios
            )
            
            # If successful, create ticket record
            if result.get('success'):
                logger.info(f"[BOOKING_SAGA_SERVICE] SAGA successful, creating ticket")
                self._create_ticket_record(user, booking_data, result)
            else:
                logger.error(f"[BOOKING_SAGA_SERVICE] SAGA failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"[BOOKING_SAGA_SERVICE] Exception: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_ticket_record(
        self,
        user: User,
        booking_data: Dict[str, Any],
        saga_result: Dict[str, Any]
    ) -> Ticket:
        """Create ticket record in database after successful SAGA"""
        try:
            # This is a placeholder - integrate with your actual ticket creation logic
            logger.info(f"[BOOKING_SAGA_SERVICE] Creating ticket record")
            
            # You would implement actual ticket creation here
            # For now, just log it
            logger.info(f"[BOOKING_SAGA_SERVICE] Ticket would be created with booking reference: {saga_result.get('booking_reference')}")
            
        except Exception as e:
            logger.error(f"[BOOKING_SAGA_SERVICE] Error creating ticket record: {e}")
    
    def get_booking_status(self) -> Dict[str, Any]:
        """Get current booking SAGA status"""
        if self.orchestrator:
            return self.orchestrator.get_saga_status()
        return {'error': 'No active SAGA'}


# Global service instance
booking_saga_service = BookingSAGAService()
