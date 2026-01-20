from django.db import models
from django.utils import timezone

class PaymentAuthorization(models.Model):
    """Payment authorization tracking for SAGA"""
    PAYMENT_STATUS_CHOICES = [
        ('AUTHORIZED', 'Authorized'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired')
    ]
    
    correlation_id = models.CharField(max_length=50)
    authorization_id = models.CharField(max_length=50, unique=True)
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