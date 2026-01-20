
from django.db import models
from django.utils import timezone

class LoyaltyAccount(models.Model):
    """User loyalty account with points balance"""
    user_id = models.CharField(max_length=20, unique=True)  # Store as string to match other services
    points_balance = models.IntegerField(default=0)
    tier_status = models.CharField(max_length=20, default='Regular')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"User {self.user_id} - {self.points_balance} points ({self.tier_status})"
    
    def calculate_tier(self):
        """Calculate tier based on points balance"""
        if self.points_balance >= 125000:
            return 'ConciergeKey'
        elif self.points_balance >= 100000:
            return 'Executive Platinum'
        elif self.points_balance >= 75000:
            return 'Platinum Pro'
        elif self.points_balance >= 50000:
            return 'Platinum'
        elif self.points_balance >= 25000:
            return 'Gold'
        else:
            return 'Regular'
    
    def miles_to_next_tier(self):
        """Calculate miles needed for next tier"""
        if self.points_balance >= 125000:
            return 0
        elif self.points_balance >= 100000:
            return 125000 - self.points_balance
        elif self.points_balance >= 75000:
            return 100000 - self.points_balance
        elif self.points_balance >= 50000:
            return 75000 - self.points_balance
        elif self.points_balance >= 25000:
            return 50000 - self.points_balance
        else:
            return 25000 - self.points_balance
    
    def save(self, *args, **kwargs):
        """Update tier status when saving"""
        self.tier_status = self.calculate_tier()
        super().save(*args, **kwargs)


class LoyaltyTransaction(models.Model):
    """Transaction history for loyalty points"""
    TRANSACTION_TYPE_CHOICES = [
        ('flight_booking', 'Flight Booking'),
        ('miles_redemption', 'Miles Redemption'),
        ('bonus_award', 'Bonus Award'),
        ('adjustment', 'Adjustment'),
    ]
    
    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=50)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    points_earned = models.IntegerField(default=0)
    points_redeemed = models.IntegerField(default=0)
    points_value = models.FloatField(default=0.0)  # Dollar value for redemptions
    amount = models.FloatField(default=0.0)  # Original transaction amount
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.points_earned > 0:
            return f"{self.account.user_id} earned {self.points_earned} points"
        else:
            return f"{self.account.user_id} redeemed {self.points_redeemed} points"


class SagaMilesAward(models.Model):
    """SAGA loyalty miles award tracking for compensation"""
    AWARD_STATUS_CHOICES = [
        ('AWARDED', 'Awarded'),
        ('REVERSED', 'Reversed')
    ]
    
    correlation_id = models.CharField(max_length=50)
    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='saga_awards')
    miles_awarded = models.IntegerField()
    original_balance = models.IntegerField()
    new_balance = models.IntegerField()
    status = models.CharField(max_length=15, choices=AWARD_STATUS_CHOICES, default='AWARDED')
    awarded_at = models.DateTimeField(auto_now_add=True)
    reversed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"SAGA Miles {self.correlation_id} - {self.miles_awarded} miles - {self.status}"