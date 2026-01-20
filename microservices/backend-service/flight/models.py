
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime

# Create your models here.

class User(AbstractUser):
    def __str__(self):
        return f"{self.pk or 'New'}: {self.first_name} {self.last_name}"

class Place(models.Model):
    city = models.CharField(max_length=64)
    airport = models.CharField(max_length=64)
    code = models.CharField(max_length=3)
    country = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.city}, {self.country} ({self.code})"


class Week(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name} ({self.number})"


class Flight(models.Model):
    origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="arrivals")
    depart_time = models.TimeField(auto_now=False, auto_now_add=False)
    depart_day = models.ManyToManyField(Week, related_name="flights_of_the_day")
    duration = models.DurationField(null=True)
    arrival_time = models.TimeField(auto_now=False, auto_now_add=False)
    plane = models.CharField(max_length=24)
    airline = models.CharField(max_length=64)
    flight_number = models.CharField(max_length=10, blank=True, null=True)  # Added flight number field
    economy_fare = models.FloatField(null=True)
    business_fare = models.FloatField(null=True)
    first_fare = models.FloatField(null=True)

    def __str__(self):
        flight_display = self.flight_number if self.flight_number else f"Flight {self.pk}"
        return f"{flight_display}: {self.origin} to {self.destination}"


GENDER = (
    ('male','MALE'),    #(actual_value, human_readable_value)
    ('female','FEMALE')
)

class Passenger(models.Model):
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER, blank=True)

    def __str__(self):
        return f"Passenger: {self.first_name} {self.last_name}, {self.gender}"


SEAT_CLASS = (
    ('economy', 'Economy'),
    ('business', 'Business'),
    ('first', 'First')
)

TICKET_STATUS =(
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELLED', 'Cancelled')
)

class Ticket(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bookings", blank=True, null=True)
    ref_no = models.CharField(max_length=6, unique=True)
    passengers = models.ManyToManyField(Passenger, related_name="flight_tickets")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets", blank=True, null=True)
    flight_ddate = models.DateField(blank=True, null=True)
    flight_adate = models.DateField(blank=True, null=True)
    flight_fare = models.FloatField(blank=True,null=True)
    other_charges = models.FloatField(blank=True,null=True)
    coupon_used = models.CharField(max_length=15,blank=True)
    coupon_discount = models.FloatField(default=0.0)
    total_fare = models.FloatField(blank=True, null=True)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS)
    booking_date = models.DateTimeField(default=timezone.now)
    mobile = models.CharField(max_length=20,blank=True)
    email = models.EmailField(max_length=45, blank=True)
    status = models.CharField(max_length=45, choices=TICKET_STATUS)

    def __str__(self):
        return self.ref_no


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
        return f"Reservation {self.correlation_id} - {self.status}"


class SagaTransaction(models.Model):
    """SAGA transaction tracking for complete audit trail"""
    SAGA_STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('COMPENSATED', 'Compensated')
    ]
    
    correlation_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_data = models.JSONField()  # Store original booking data
    status = models.CharField(max_length=15, choices=SAGA_STATUS_CHOICES, default='STARTED')
    steps_completed = models.IntegerField(default=0)
    failed_step = models.CharField(max_length=50, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    compensation_executed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SAGA {self.correlation_id} - {self.status}"


class SagaPaymentAuthorization(models.Model):
    """SAGA payment authorization tracking"""
    PAYMENT_STATUS_CHOICES = [
        ('AUTHORIZED', 'Authorized'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired')
    ]
    
    correlation_id = models.CharField(max_length=50)
    authorization_id = models.CharField(max_length=50)
    amount = models.FloatField()
    flight_fare = models.FloatField()
    other_charges = models.FloatField()
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='AUTHORIZED')
    payment_method = models.CharField(max_length=20, default='mock_card')
    authorized_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.authorization_id} - {self.status}"


class SagaMilesAward(models.Model):
    """SAGA loyalty miles award tracking"""
    AWARD_STATUS_CHOICES = [
        ('AWARDED', 'Awarded'),
        ('REVERSED', 'Reversed')
    ]
    
    correlation_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=20)  # Store as string to match loyalty service
    miles_awarded = models.IntegerField()
    original_balance = models.IntegerField()
    new_balance = models.IntegerField()
    status = models.CharField(max_length=15, choices=AWARD_STATUS_CHOICES, default='AWARDED')
    awarded_at = models.DateTimeField(auto_now_add=True)
    reversed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Miles {self.correlation_id} - {self.miles_awarded} miles - {self.status}"
