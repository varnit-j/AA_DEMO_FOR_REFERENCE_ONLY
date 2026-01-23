
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.loyalty.models import LoyaltyTier, LoyaltyAccount, PointsTransaction
from apps.loyalty.service import LoyaltyService

User = get_user_model()


class LoyaltyTierTestCase(TestCase):
    """Test cases for LoyaltyTier model"""
    
    def setUp(self):
        self.bronze_tier = LoyaltyTier.objects.create(
            name='bronze',
            display_name='Bronze',
            min_points_required=0,
            points_multiplier=Decimal('1.00'),
            redemption_bonus=Decimal('1.00')
        )
        self.silver_tier = LoyaltyTier.objects.create(
            name='silver',
            display_name='Silver',
            min_points_required=1000,
            points_multiplier=Decimal('1.25'),
            redemption_bonus=Decimal('1.10')
        )
    
    def test_tier_creation(self):
        """Test tier creation and string representation"""
        self.assertEqual(str(self.bronze_tier), "Bronze (min: 0 pts)")
        self.assertEqual(str(self.silver_tier), "Silver (min: 1000 pts)")
    
    def test_tier_ordering(self):
        """Test tiers are ordered by min_points_required"""
        tiers = list(LoyaltyTier.objects.all())
        self.assertEqual(tiers[0], self.bronze_tier)
        self.assertEqual(tiers[1], self.silver_tier)


class LoyaltyAccountTestCase(TestCase):
    """Test cases for LoyaltyAccount model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.bronze_tier = LoyaltyTier.objects.create(
            name='bronze',
            display_name='Bronze',
            min_points_required=0,
            points_multiplier=Decimal('1.00'),
            redemption_bonus=Decimal('1.00')
        )
        self.account = LoyaltyAccount.objects.create(
            user=self.user,
            current_tier=self.bronze_tier,
            current_points_balance=500,
            total_points_earned=500
        )
    
    def test_account_creation(self):
        """Test account creation and relationships"""
        self.assertEqual(self.account.user, self.user)
        self.assertEqual(self.account.current_tier, self.bronze_tier)
        self.assertEqual(self.account.current_points_balance, 500)
    
    def test_get_effective_multiplier(self):
        """Test tier multiplier retrieval"""
        self.assertEqual(self.account.get_effective_multiplier(), Decimal('1.00'))
    
    def test_get_redemption_bonus(self):
        """Test redemption bonus retrieval"""
        self.assertEqual(self.account.get_redemption_bonus(), Decimal('1.00'))


class LoyaltyServiceTestCase(TestCase):
    """Test cases for LoyaltyService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.bronze_tier = LoyaltyTier.objects.create(
            name='bronze',
            display_name='Bronze',
            min_points_required=0,
            points_multiplier=Decimal('1.00'),
            redemption_bonus=Decimal('1.00')
        )
        