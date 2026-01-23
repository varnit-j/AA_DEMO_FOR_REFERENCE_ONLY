
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from apps.orders.models import Order
from apps.payments.stripe_client import StripeClient

User = get_user_model()


class StripeClientTestCase(TestCase):
    """Test cases for StripeClient"""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_create):
        """Test PaymentIntent creation"""
        
        # Mock Stripe response
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = 'pi_test123'
        mock_payment_intent.client_secret = 'pi_test123_secret'
        mock_payment_intent.status = 'requires_payment_method'
        mock_payment_intent.metadata = {'order_id': 'test-order'}
        mock_create.return_value = mock_payment_intent
        
        result = StripeClient.create_payment_intent(
            amount=Decimal('100.00'),
            metadata={'order_id': 'test-order'}
        )
        
        self.assertEqual(result['id'], 'pi_test123')
        self.assertEqual(result['client_secret'], 'pi_test123_secret')
        self.assertEqual(result['amount'], Decimal('100.00'))
        
        # Verify Stripe was called with correct parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args['amount'], 10000)  # $100 in cents
        self.assertEqual(call_args['currency'], 'usd')
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_create):
        """Test Checkout Session creation"""
        
        # Mock Stripe response
        mock_session = MagicMock()
        mock_session.id = 'cs_test123'
        mock_session.url = 'https://checkout.stripe.com/pay/cs_test123'
        mock_session.payment_status = 'unpaid'
        mock_session.metadata = {'order_id': 'test-order'}
        mock_create.return_value = mock_session
        
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Test Product'},
                'unit_amount': 10000,
            },
            'quantity': 1,
        }]
        
        result = StripeClient.create_checkout_session(
            line_items=line_items,
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )
        
        self.assertEqual(result['id'], 'cs_test123')
        self.assertEqual(result['url'], 'https://checkout.stripe.com/pay/cs_test123')
        
        mock_create.assert_called_once()


class PaymentViewsTestCase(TestCase):
    """Test cases for payment views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('500.00'),
            cash_amount=Decimal('500.00'),
            payment_method='cash_only',
            status='draft'
        )
    
    def test_create_payment_intent_requires_login(self):
        """Test that payment intent creation requires authentication"""
        
        response = self.client.post('/payments/create-intent',
                                  data=json.dumps({'order_id': str(self.order.id)}),
                                  content_type='application/json')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    @patch('apps.payments.stripe_client.StripeClient.create_payment_intent')
    def test_create_payment_intent_success(self, mock_create):
        """Test successful payment intent creation"""
        
        # Mock Stripe response
        mock_create.return_value = {
            'id': 'pi_test123',
            'client_secret': 'pi_test123_secret',
            'amount': Decimal('500.00'),
            'currency': 'usd'
        }
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/payments/create-intent',
                                  data=json.dumps({'order_id': str(self.order.id)}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['payment_intent_id'], 'pi_test123')
        self.assertEqual(data['amount'], 500.0)
        
        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending_payment')