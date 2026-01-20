
"""
Complete seat allocation utilities for automatic seat reservation
Handles 162 seats per flight: Economy (4A-27F), Business (1A-3F), First (1A-2F)
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import Flight, Seat, SeatReservation, User

logger = logging.getLogger(__name__)

class SeatAllocationError(Exception):
    """Custom exception for seat allocation errors"""
    pass

def get_available_seats(flight, seat_class='economy', count=1):
    """Get available seats for a flight by class"""
    try:
        available_seats = Seat.objects.filter(
            flight=flight,
            seat_class=seat_class,
            is_available=True
        ).order_by('seat_number')
        
        logger.info(f"Found {available_seats.count()} available {seat_class} seats for flight {flight.flight_number}")
        
        if available_seats.count() < count:
            raise SeatAllocationError(f"Not enough {seat_class} seats available. Requested: {count}, Available: {available_seats.count()}")
        
        return list(available_seats[:count])
        
    except Exception as e:
        logger.error(f"Error getting available seats: {e}")
        raise SeatAllocationError(f"Failed to get available seats: {str(e)}")

@transaction.atomic
def reserve_seats_for_saga(correlation_id, flight_id, passenger_count, seat_class='economy', user_id=None):
    """Reserve seats for SAGA transaction with automatic allocation"""
    try:
        logger.info(f"[SAGA] Reserving {passenger_count} {seat_class} seats for flight {flight_id}, correlation_id: {correlation_id}")
        
        # Get flight
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            raise SeatAllocationError(f"Flight {flight_id} not found")
        
        # Check if reservation already exists
        existing_reservation = SeatReservation.objects.filter(correlation_id=correlation_id).first()
        if existing_reservation:
            logger.warning(f"Reservation already exists for correlation_id: {correlation_id}")
            return {
                'success': True,
                'reservation_id': existing_reservation.id,
                'correlation_id': correlation_id,
                'seats_reserved': existing_reservation.seats.count(),
                'message': 'Seats already reserved for this transaction'
            }
        
        # Get available seats
        available_seats = get_available_seats(flight, seat_class, passenger_count)
        
        # Get user if provided
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found, proceeding without user")
        
        # Create reservation with expiry (15 minutes from now)
        expiry_time = timezone.now() + timedelta(minutes=15)
        
        reservation = SeatReservation.objects.create(
            correlation_id=correlation_id,
            flight=flight,
            user=user,
            status='RESERVED',
            expires_at=expiry_time
        )
        
        # Mark seats as unavailable and add to reservation
        seat_numbers = []
        for seat in available_seats:
            seat.is_available = False
            seat.save()
            reservation.seats.add(seat)
            seat_numbers.append(seat.seat_number)
        
        logger.info(f"[SAGA] Successfully reserved seats {seat_numbers} for correlation_id: {correlation_id}")
        
        return