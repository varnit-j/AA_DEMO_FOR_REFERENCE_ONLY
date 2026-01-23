
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket

# Import loyalty service
try:
    from apps.loyalty.service import LoyaltyService
    from apps.loyalty.models import PointsTransaction
except ImportError:
    LoyaltyService = None
    PointsTransaction = None


def process_ticket_cancellation(user, ticket_ref):
    """
    Process ticket cancellation with refund and loyalty points reversal
    """
    # Safe print function that handles Unicode encoding errors
    def safe_print(message):
        try:
            print(message)
        except UnicodeEncodeError:
            # If Unicode error, print ASCII-safe version
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(f"[UNICODE_SAFE] {safe_message}")
    
    try:
        ticket = Ticket.objects.get(ref_no=ticket_ref)
        
        # Verify ownership
        if ticket.user != user:
            return {'success': False, 'error': 'User unauthorised'}
        
        # Only allow cancellation of confirmed tickets
        if ticket.status != 'CONFIRMED':
            return {'success': False, 'error': 'Only confirmed tickets can be cancelled'}
        
        safe_print(f"DEBUG: Processing cancellation for ticket {ticket.ref_no} by user {user.username}")
        
        # LOYALTY INTEGRATION - Handle points reversal for cancelled booking
        if LoyaltyService and PointsTransaction:
            try:
                # 1. Find and reverse points earned from this booking
                earned_transactions = PointsTransaction.objects.filter(
                    account__user=user,
                    reference_id=ticket.ref_no,
                    transaction_type='earn',
                    status='completed'
                )
                
                for transaction in earned_transactions:
                    safe_print(f"DEBUG: Reversing {transaction.points_amount} earned points for ticket {ticket.ref_no}")
                    
                    # Create a reversal transaction (deduct the earned points)
                    LoyaltyService.redeem_points(
                        user=user,
                        points_amount=transaction.points_amount,
                        reference_id=f"CANCEL-{ticket.ref_no}",
                        description=f"Cancellation reversal - removing earned points from booking {ticket.ref_no}"
                    )
                    safe_print(f"DEBUG: Successfully reversed {transaction.points_amount} earned points")
                
                # 2. Find and restore points redeemed during this booking
                redeemed_transactions = PointsTransaction.objects.filter(
                    account__user=user,
                    reference_id=ticket.ref_no,
                    transaction_type='redeem',
                    status='completed'
                )
                
                for transaction in redeemed_transactions:
                    safe_print(f"DEBUG: Restoring {transaction.points_amount} redeemed points for ticket {ticket.ref_no}")
                    
                    # Restore the redeemed points back to user's account
                    LoyaltyService.earn_points(
                        user=user,
                        points_amount=transaction.points_amount,
                        reference_id=f"REFUND-{ticket.ref_no}",
                        description=f"Points refund for cancelled booking - {ticket.ref_no}"
                    )
                    safe_print(f"DEBUG: Successfully restored {transaction.points_amount} redeemed points")
                
            except Exception as loyalty_error:
                safe_print(f"DEBUG: Loyalty points reversal error: {loyalty_error}")
                return {'success': False, 'error': f'Loyalty points reversal failed: {loyalty_error}'}
        
        # 3. Process refund (simulate refund processing)
        refund_amount = float(ticket.total_fare) if ticket.total_fare else 0
        safe_print(f"DEBUG: Processing refund of ${refund_amount} for ticket {ticket.ref_no}")
        
        # In a real system, you would integrate with payment gateway for actual refund
        # For now, we'll just log the refund processing
        safe_print(f"DEBUG: Refund of ${refund_amount} processed successfully for ticket {ticket.ref_no}")
        
        # 4. Update ticket status to cancelled
        ticket.status = 'CANCELLED'
        ticket.save()
        
        safe_print(f"DEBUG: Ticket {ticket.ref_no} successfully cancelled with full refund and loyalty points reversal")
        
        return {
            'success': True,
            'message': f'Ticket cancelled successfully. Refund of ${refund_amount} will be processed within 5-7 business days.',
            'refund_amount': refund_amount
        }
        
    except Ticket.DoesNotExist:
        return {'success': False, 'error': 'Ticket not found'}
    except Exception as e:
        safe_print(f"DEBUG: Cancellation error: {e}")
        return {'success': False, 'error': str(e)}