"""
Seat Management Models for SAGA Pattern
Handles seat reservations and availability
"""
from django.db import models
from .models import Flight, User

class Seat(models.Model):
    """Individual seat on a flight"""
    SEAT_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'), 
        ('first', 'First')
    ]
    
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=4)  # e.g., "12A", "5F"
    seat_class = models.CharField(max_length=10, choices=SEAT_CLASS_CHOICES)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['flight', 'seat_number']
    
    def __str__(self):
        return f"{self.flight.flight_number} - {self.seat_number} ({self.seat_class})"

class SeatReservation(models.Model):
    """SAGA seat reservation tracking"""
    RESERVATION_STATUS_CHOICES = [
        ('RESERVED', 'Reserved'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired')
    ]
    
    correlation_id = models.CharField(max_length=50, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=RESERVATION_STATUS_CHOICES, default='RESERVED')
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Reservation expiry
    
    def __str__(self):
    def __str__(self):
