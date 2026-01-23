def saga_results(request):
    """SAGA Results page showing detailed failure information and logs"""
    if request.user.is_authenticated:
        correlation_id = request.GET.get('correlation_id', 'unknown')
        is_demo = request.GET.get('demo') == 'true'
        
        print(f"[DEBUG] SAGA Results - Correlation ID: {correlation_id}, Demo: {is_demo}")
        
        # Get SAGA transaction details from backend
        saga_status = None
        if correlation_id != 'unknown':
            saga_status = call_backend_api(f'api/saga/status/{correlation_id}/')
            print(f"[DEBUG] SAGA Results - Backend API returned: {saga_status}")
        
        # If no saga_status from backend or correlation_id is unknown, provide demo data
        if not saga_status:
            print(f"[DEBUG] SAGA Results - No backend data, providing demo saga_status")
            # Generate a demo correlation ID if unknown
            if correlation_id == 'unknown':
                import uuid
                correlation_id = str(uuid.uuid4())[:8]
                print(f"[DEBUG] SAGA Results - Generated demo correlation_id: {correlation_id}")
            
            # Provide demo SAGA status data for display
            saga_status = {
                'correlation_id': correlation_id,
                'status': 'failed',
                'failed_step': 'AuthorizePayment',  # Demo failure at payment step
                'steps_completed': 1,  # Completed seat reservation
                'compensations_executed': 1,  # Compensated seat reservation
                'total_steps': 4,
                'error': 'Simulated payment authorization failure for demo purposes',
                'compensation_details': [
                    {'step': 'ReserveSeat', 'status': 'compensated', 'message': 'Seat reservation cancelled'}
                ]
            }
        
        # Get user's current loyalty points for compensation display
        user_loyalty = loyalty_tracker.get_user_points(request.user.id)
        user_points = user_loyalty.get('points_balance', 0)
        
        # Get recent transactions to show what was compensated
        transaction_history = loyalty_tracker.get_user_transactions(request.user.id)
        recent_transactions = transaction_history[-5:] if transaction_history else []
        
        context = {
            'correlation_id': correlation_id,
            'is_demo': is_demo,
            'saga_status': saga_status,
            'user_points': user_points,
            'recent_transactions': recent_transactions,
            'page': 'saga_results'
        }
        
        print(f"[DEBUG] SAGA Results - Final context: correlation_id={correlation_id}, saga_status keys={list(saga_status.keys()) if saga_status else 'None'}")
        return render(request, 'flight/saga_results.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))