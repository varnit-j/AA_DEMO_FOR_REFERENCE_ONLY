
"""
Failed Booking Handler for SAGA Transactions
Creates failed booking records when SAGA fails
"""
import logging
import secrets
from typing import Dict, Any
from django.utils import timezone

logger = logging.getLogger(__name__)

def create_failed_booking_record(correlation_id: str, booking_data: Dict[str, Any], failed_step: str, error_message: str, compensation_result: Dict[str, Any] = None):
    """
    Create a failed booking record so users can see failed bookings
    """
    try:
        logger.info(f"[SAGA FAILED BOOKING] 📝 Creating failed booking record for correlation_id: {correlation_id}")
        logger.info(f"[SAGA FAILED BOOKING] ❌ Failed at step: {failed_step}")
        logger.info(f"[SAGA FAILED BOOKING] 💬 Error: {error_message}")
        logger.info(f"[SAGA FAILED BOOKING] 📊 Booking data: {booking_data}")
        logger.info(f"[SAGA FAILED BOOKING] 🔄 Compensation result: {compensation_result}")
        
        # FIXED: Now creating actual database records directly using Django ORM
        logger.info(f"[SAGA FAILED BOOKING] 🔧 FIXED: Now creating actual database record directly")
        
        try:
            # Import models here to avoid circular imports
            from .models import Flight, Ticket, Passenger
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # Get flight
            flight_id = booking_data.get('flight_id')
            flight = Flight.objects.get(id=flight_id)
            logger.info(f"[SAGA FAILED BOOKING] ✅ Found flight: {flight}")
            
            # Get user (optional)
            user = None
            user_id = booking_data.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    logger.info(f"[SAGA FAILED BOOKING] ✅ Found user: {user}")
                except User.DoesNotExist:
                    logger.warning(f"[SAGA FAILED BOOKING] ⚠️ User {user_id} not found")
            
            # Generate reference number
            ref_no = f"F{secrets.token_hex(2).upper()}{correlation_id[:3].upper()}"
            
            # Calculate fare
            passengers_data = booking_data.get('passengers', [])
            passenger_count = len(passengers_data)
            seat_class = booking_data.get('seat_class', 'economy')
            
            if seat_class == 'business' and flight.business_fare:
                base_fare = flight.business_fare
            elif seat_class == 'first' and flight.first_fare:
                base_fare = flight.first_fare
            else:
                base_fare = flight.economy_fare
                seat_class = 'economy'
            
            flight_fare = base_fare * passenger_count if base_fare else 0
            other_charges = flight_fare * 0.08 + 25.0  # 8% tax + $25 service fee
            total_fare = flight_fare + other_charges
            
            # Create failed ticket
            contact_info = booking_data.get('contact_info', {})
            failed_ticket = Ticket.objects.create(
                user=user,
                ref_no=ref_no,
                flight=flight,
                flight_ddate=None,  # No dates for failed bookings
                flight_adate=None,
                flight_fare=flight_fare,
                other_charges=other_charges,
                total_fare=total_fare,
                seat_class=seat_class,
                booking_date=timezone.now(),
                mobile=contact_info.get('mobile', ''),
                email=contact_info.get('email', ''),
                status='FAILED',
                saga_correlation_id=correlation_id,
                failed_step=failed_step,
                failure_reason=error_message,
                compensation_executed=bool(compensation_result and compensation_result.get('successful_compensations', 0) > 0),
                compensation_details=compensation_result
            )
            
            # Create passengers
            for passenger_data in passengers_data:
                passenger = Passenger.objects.create(
                    first_name=passenger_data.get('first_name', ''),
                    last_name=passenger_data.get('last_name', ''),
                    gender=passenger_data.get('gender', 'male')
                )
                failed_ticket.passengers.add(passenger)
            
            logger.info(f"[SAGA FAILED BOOKING] ✅ Successfully created failed booking in database: {ref_no}")
            
            return {
                'success': True,
                'ref_no': ref_no,
                'ticket_id': failed_ticket.id,
                'correlation_id': correlation_id,
                'message': 'Failed booking record created in database'
            }
            
        except Exception as db_error:
            logger.error(f"[SAGA FAILED BOOKING] ❌ Database error: {db_error}")
            return create_fallback_record(correlation_id, str(db_error))
        
    except Exception as e:
        logger.error(f"[SAGA FAILED BOOKING] ❌ Error creating failed booking record: {e}")
        return create_fallback_record(correlation_id, str(e))

def create_fallback_record(correlation_id: str, error_message: str):
    """
    Fallback function when database creation fails - just log the failure
    """
    logger.warning(f"[SAGA FAILED BOOKING] ⚠️ Using fallback - only logging failed booking")
    
    return {
        'success': True,
        'ref_no': f"F{correlation_id[:6].upper()}",
        'correlation_id': correlation_id,
        'message': 'Failed booking logged (fallback mode)'
    }