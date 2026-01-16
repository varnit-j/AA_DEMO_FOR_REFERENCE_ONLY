from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .service import LoyaltyService
from .models import LoyaltyTier


@login_required
def loyalty_dashboard(request):
    """Display user's loyalty dashboard with points balance and tier info"""
    try:
        account = LoyaltyService.get_or_create_account(request.user)
        recent_transactions = LoyaltyService.get_transaction_history(request.user, limit=10)
        
        context = {
            'account': account,
            'recent_transactions': recent_transactions,
            'available_tiers': LoyaltyTier.objects.all().order_by('min_points_required'),
        }
        return render(request, 'loyalty/dashboard.html', context)
    except Exception as e:
        return render(request, 'loyalty/dashboard.html', {
            'error': f'Error loading loyalty dashboard: {str(e)}'
        })


@login_required
def points_history(request):
    """Display detailed points transaction history"""
    try:
        transactions = LoyaltyService.get_transaction_history(request.user, limit=50)
        account = LoyaltyService.get_or_create_account(request.user)
        
        context = {
            'transactions': transactions,
            'account': account,
        }
        return render(request, 'loyalty/points_history.html', context)
    except Exception as e:
        return render(request, 'loyalty/points_history.html', {
            'error': f'Error loading points history: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def calculate_points_value(request):
    """AJAX endpoint to calculate points value for redemption"""
    try:
        data = json.loads(request.body)
        points_amount = int(data.get('points_amount', 0))
        
        if points_amount <= 0:
            return JsonResponse({'error': 'Invalid points amount'}, status=400)
        
        account = LoyaltyService.get_or_create_account(request.user)
        
        if account.current_points_balance < points_amount:
            return JsonResponse({
                'error': 'Insufficient points balance',
                'available_points': account.current_points_balance
            }, status=400)
        
        points_value = LoyaltyService.calculate_points_value(
            points_amount, 
            account.current_tier
        )
        
        return JsonResponse({
            'success': True,
            'points_amount': points_amount,
            'points_value': float(points_value),
            'available_points': account.current_points_balance,
            'tier': account.current_tier.display_name if account.current_tier else 'No Tier'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def tier_info(request):
    """Display information about loyalty tiers"""
    try:
        account = LoyaltyService.get_or_create_account(request.user)
        tiers = LoyaltyTier.objects.all().order_by('min_points_required')
        
        context = {
            'account': account,
            'tiers': tiers,
        }
        return render(request, 'loyalty/tier_info.html', context)
    except Exception as e:
        return render(request, 'loyalty/tier_info.html', {
            'error': f'Error loading tier information: {str(e)}'
        })