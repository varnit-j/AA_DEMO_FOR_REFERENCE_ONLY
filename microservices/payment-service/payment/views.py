
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import stripe
import os

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder')

@csrf_exempt
@require_http_methods(["POST"])
def process_payment(request):
    """Process payment through Stripe"""
    try:
        data = json.loads(request.body)
        
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        payment_method = data.get('payment_method_id')
        
        if not amount or not payment_method:
            return JsonResponse({'error': 'Amount and payment method are required'}, status=400)
        
        # Create payment intent with Stripe
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe expects cents
                currency=currency,
                payment_method=payment_method,
                confirm=True,
                return_url='http://localhost:8000/payment/success'
            )
            
            return JsonResponse({
                'success': True,
                'payment_id': intent.id,
                'status': intent.status,
                'amount': amount,
                'currency': currency
            })
            
        except Exception as e:
            if 'card' in str(e).lower():
                return JsonResponse({'error': f'Card error: {str(e)}'}, status=400)
            else:
                return JsonResponse({'error': f'Payment error: {str(e)}'}, status=500)
        
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        return JsonResponse({'error': 'Payment processing failed'}, status=500)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if endpoint_secret:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except ValueError:
                return HttpResponse(status=400)
            except Exception:
                return HttpResponse(status=400)
        else:
            event = json.loads(payload)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded: {payment_intent['id']}")
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.info(f"Payment failed: {payment_intent['id']}")
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=400)

@require_http_methods(["GET"])
def payment_status(request, payment_id):
    """Get payment status"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_id)
        return JsonResponse({
            'payment_id': payment_id,
            'status': intent.status,
            'amount': intent.amount / 100,  # Convert from cents
            'currency': intent.currency
        })
    except Exception as e:
        return JsonResponse({'error': 'Payment not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def process_refund(request):
    """Process payment refund"""
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        amount = data.get('amount')
        
        if not payment_id:
            return JsonResponse({'error': 'Payment ID is required'}, status=400)
        
        # Create refund with Stripe
        try:
            refund_params = {'payment_intent': payment_id}
            if amount:
                refund_params['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return JsonResponse({
                'success': True,
                'refund_id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100,
                'payment_id': payment_id
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Refund error: {str(e)}'}, status=500)
        
    except Exception as e:
        logger.error(f"Refund processing error: {e}")
        return JsonResponse({'error': 'Refund processing failed'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def validate_card(request):
    """Validate card through mock banking system"""
    try:
        data = json.loads(request.body)
        card_number = data.get('card_number')
        cvv = data.get('cvv')
        expiry_month = data.get('expiry_month')
        expiry_year = data.get('expiry_year')
        
        if not all([card_number, cvv, expiry_month, expiry_year]):
            return JsonResponse({'error': 'All card details are required'}, status=400)
        
        # Mock card validation
        return JsonResponse({
            'valid': True,
            'card_type': 'visa',
            'last_four': card_number[-4:] if len(card_number) >= 4 else '****'
        })
        
    except Exception as e:
        logger.error(f"Card validation error: {e}")
        return JsonResponse({'error': 'Card validation failed'}, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'payment-service'})