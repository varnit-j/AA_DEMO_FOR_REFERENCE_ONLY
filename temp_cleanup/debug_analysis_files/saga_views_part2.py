
"""
SAGA Views Part 2 - Compensation methods
"""

@csrf_exempt
@require_http_methods(["POST"])
def confirm_booking_complete(request):
    """Complete the confirm booking method"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        simulate_failure = data.get('simulate_failure', False)
        
        logger.info(f"[SAGA] ConfirmBooking step for correlation_id: {correlation_id}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA] Simulated failure in ConfirmBooking for {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": "Simulated booking confirmation failure"
            })
        
        # Check if reservation exists
        if correlation_id not in saga_reservations:
            return JsonResponse({
                "success": False,
                "error": f"No reservation found for correlation_id: {correlation_id}"
            })
        
        reservation = saga_reservations[correlation_id]
        
        # Create actual ticket
        flight = Flight.objects.get(id=reservation['flight_id'])
        
        # Get or create user
        user_id = booking_data.get('user_id', 1)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.get(id=1)  # Fallback
        
        # Generate reference number
        import secrets
        ref_no = secrets.token_hex(3).upper()
        
        # Create ticket
        ticket = Ticket.objects.create(
            user=user,
            ref_no=ref_no,
            flight=flight,
            flight_ddate=booking_data.get('flight_date', '2024-01-15'),
            flight_adate=booking_data.get('flight_date', '2024-01-15'),
            flight_fare=flight.economy_fare,
            other_charges=50.0,
            total_fare=flight.economy_fare + 50.0,
            seat_class='economy',
            mobile=booking_data.get('contact_info', {}).get('mobile', ''),
            email=booking_data.get('contact_info', {}).get('email', ''),
            status='CONFIRMED'
        )
        
        # Create passengers
        passengers = []
        for passenger_data in reservation['passengers']:
            passenger = Passenger.objects.create(
                first_name=passenger_data.get('first_name', ''),
                last_name=passenger_data.get('last_name', ''),
                gender=passenger_data.get('gender', 'male')
            )
            passengers.append(passenger)
        
        ticket.passengers.set(passengers)
        
        # Update reservation status
        saga_reservations[correlation_id]['status'] = 'CONFIRMED'
        saga_reservations[correlation_id]['ticket_id'] = ticket.id
        saga_reservations[correlation_id]['ref_no'] = ref_no
        
        logger.info(f"[SAGA] Booking confirmed successfully. Ticket: {ref_no}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "ticket_id": ticket.id,
            "ref_no": ref_no,
            "status": "CONFIRMED"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ConfirmBooking: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_