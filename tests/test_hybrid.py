
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from flight.models import Ticket, Flight, Place, Week
from apps.orders.models import Order
from apps.loyalty.models import LoyaltyTier, LoyaltyAccount
# from flight.views.hybrid_checkout import calculate_hybrid_pricing, process_hybrid_redemption

User = get_user_model()


class HybridCheckoutTestCase(TestCase):
    """Test cases for hybrid checkout functionality"""
    
    def setUp(self):
        self.client = Client()
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
            current_points_balance=5000,
            total_points_earned=5000
        )
        
        # Create flight and ticket
        self.origin = Place.objects.create(
            city='New York',
            airport='John F. Kennedy International',
            code='JFK',
            country='USA'
        )
        
        self.destination = Place.objects.create(
            city='Los Angeles',
            airport='Los Angeles International',
            code='LAX',
            country='USA'
        )
        
        self.week = Week.objects.create(number=0, name='Monday')
        
        self.flight = Flight.objects.create(
            origin=self.origin,
            destination=self.destination,
            depart_time='10:00:00',
            arrival_time='13:00:00',
            plane='Boeing 737',
            airline='Test Airlines',
            economy_fare=Decimal('500.00')
        )
        self.flight.depart_day.add(self.week)
        
        self.ticket = Ticket.objects.create(
            user=self.user,
            ref_no='TEST123',
            flight=self.flight,
            total_fare=Decimal('600.00'),
            seat_class='economy',
            status='CONFIRMED'
        )
    
    def test_hybrid_checkout_page_requires_login(self):
        """Test that hybrid checkout page requires authentication"""
        
        response = self.client.get(f'/checkout/hybrid/{self.ticket.pk}/')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_hybrid_checkout_page_authenticated(self):
        """Test hybrid checkout page for authenticated user"""
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(f'/checkout/hybrid/{self.ticket.pk}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hybrid Payment')
        self.assertContains(response, 'Available Points: 5,000')
    
    def test_calculate_hybrid_pricing_ajax(self):
        """Test hybrid pricing calculation via AJAX"""
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/checkout/hybrid/calculate/',
                                  data=json.dumps({
                                      'ticket_id': self.ticket.pk,
                                      'points_to_use': 1000
                                 }),
                                 content_type='application/json')
       
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['pricing']['points_used'], 1000)
        self.assertEqual(data['pricing']['points_value'], 10.0)  # 1000 * 0.01
        self.assertEqual(data['pricing']['cash_amount'], 590.0)  # 600 - 10
   
    def test_insufficient_points_error(self):
        """Test error when trying to use more points than available"""
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/checkout/hybrid/calculate/',
                                  data=json.dumps({
                                      'ticket_id': self.ticket.pk,
                                      'points_to_use': 10000  # More than available
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Should use only available points (5000)
        self.assertEqual(data['pricing']['points_used'], 5000)