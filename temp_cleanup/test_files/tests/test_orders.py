
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.orders.models import Order
from apps.orders.service import OrderService
from flight.models import Ticket, Flight, Place, Week
from apps.loyalty.models import LoyaltyTier, LoyaltyAccount

User = get_user_model()


class OrderModelTestCase(TestCase):
    """Test cases for Order model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_order_creation(self):
        """Test order creation and number generation"""
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('500.00'),
            payment_method='cash_only'
        )
        
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith('ORD'))
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'draft')
    
    def test_hybrid_payment_properties(self):
        """Test hybrid payment properties"""
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('500.00'),
            payment_method='hybrid',
            points_used=1000,
            points_value=Decimal('100.00'),
            cash_amount=Decimal('400.00')
        )
        
        self.assertEqual(order.payment_method, 'hybrid')
        self.assertEqual(order.cash_amount, Decimal('400.00'))


class OrderServiceTestCase(TestCase):
    """Test cases for OrderService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create loyalty tier and account
        self.bronze_tier = LoyaltyTier.objects.create(
            name='bronze',
            display_name='Bronze',
            min_points_required=0,
            points_multiplier=Decimal('1.00'),
            redemption_bonus=Decimal('1.00')
        )
        
        self.loyalty_account = LoyaltyAccount.objects.create(
            user=self.user,
            current_tier=self.bronze_tier,
            current_points_balance=2000,
            total_points_earned=2000
        )
    
    def test_calculate_hybrid_pricing(self):
        """Test hybrid pricing calculations"""
        total_amount = Decimal('500.00')
        points_to_use = 1000
        
        pricing = OrderService.calculate_hybrid_pricing(
            self.user, 
            total_amount, 
            points_to_use
        )
        
        self.assertEqual(pricing['total_amount'], total_amount)
        self.assertEqual(pricing['points_used'], points_to_use)
        self.assertEqual(pricing['points_value'], Decimal('10.00'))  # 1000 * 0.01
        self.assertEqual(pricing['cash_amount'], Decimal('490.00'))
        self.assertEqual(pricing['savings'], Decimal('10.00'))
    
    def test_calculate_points_value(self):
        """Test points value calculation"""
        points_value = OrderService._calculate_points_value(self.user, 1000)
        self.assertEqual(points_value, Decimal('10.00'))  # 1000 * 0.01 * 1.00 (bronze bonus)
    
    def test_insufficient_points(self):
        """Test pricing with insufficient points"""
        total_amount = Decimal('500.00')
        points_to_use = 5000  # More than available
        
        pricing = OrderService.calculate_hybrid_pricing(
            self.user,
            total_amount,
            points_to_use
        )
        
        # Should only use available points (2000)
        self.assertEqual(pricing['points_used'], 2000)
        self.assertEqual(pricing['points_value'], Decimal('20.00'))
        self.assertEqual(pricing['cash_amount'], Decimal('480.00'))