"""
Seat management utilities for SAGA pattern
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import Flight, Seat, SeatReservation, User

logger = logging.getLogger(__name__)

class SeatAllocationError(Exception):
    pass

@transaction.atomic
def reserve_seats_for_saga(correlation_id, flight_id, passenger_count, seat_class='economy', user_id=None):
    """Reserve seats for SAGA transaction"""
    try:
        logger.info(f"[SAGA] Reserving {passenger_count} seats for flight {flight_id}")
        
        flight = Flight.objects.get(id=flight_id)
        
        # Check existing reservation
        existing = SeatReservation.objects.filter(correlation_id=correlation_id).first()
        if existing:
            return {'success': True, 'message': 'Already reserved'}
        
        # Get available seats
        available_seats = Seat.objects.filter(
            flight=flight,
            seat_class=seat_class,
            is_available=True
        )[:passenger_count]
        
        if len(available_seats) < passenger_count:
            raise SeatAllocationError(f"Not enough seats available")
        
        # Create reservation
        user = User.objects.get(id=user_id) if user_id else None
        reservation = SeatReservation.objects.create(
            correlation_id=correlation_id,
            flight=flight,
            user=user,
            status='RESERVED',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # Reserve seats
        seat_numbers = []
        for seat in available_seats:
            seat.is_available = False
            seat.save()
            reservation.seats.add(seat)
            seat_numbers.append(seat.seat_number)
        
        return {
            'success': True,
            'correlation_id': correlation_id,
            'seats_reserved': len(seat_numbers),
            'seat_numbers': seat_numbers
        }
        
    except Exception as e:
        logger.error(f"[SAGA] Error reserving seats: {e}")
        raise SeatAllocationError(str(e))

@transaction.atomic
def release_seats_for_saga(correlation_id):
    """Release seats for SAGA compensation"""
    try:
        logger.info(f"[SAGA] Releasing seats for {correlation_id}")
        
        reservation = SeatReservation.objects.filter(correlation_id=correlation_id).first()
        if not reservation:
            return {'success': True, 'message': 'No reservation found'}
        
        # Release seats
        for seat in reservation.seats.all():
            seat.is_available = True
            seat.save()
        
        reservation.status = 'CANCELLED'
        reservation.save()
        
        return {'success': True, 'message': 'Seats released'}
        
    except Exception as e:
        logger.error(f"[SAGA] Error releasing seats: {e}")
        return {'success': False, 'error': str(e)}

@transaction.atomic
def confirm_seat_reservation(correlation_id):
    """Confirm seat reservation"""
    try:
        reservation = SeatReservation.objects.get(correlation_id=correlation_id)
        reservation.status = 'CONFIRMED'
        reservation.save()
        return {'success': True, 'message': 'Reservation confirmed'}
    except Exception as e:
        logger.error(f"[SAGA] Error confirming reservation: {e}")
        return {'success': False, 'error': str(e)}