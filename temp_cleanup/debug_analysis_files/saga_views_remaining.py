
"""
Remaining SAGA Views - Individual Step Implementations
"""

@csrf_exempt
@require_http_methods(["POST"])
def reserve_seat(request):
    """SAGA Step 1: Reserve seat for booking"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        simulate_failure = data.get('simulate_failure', False)
        
        logger.info(f"[SAGA] ReserveSeat step for correlation_id: {correlation_id}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA] Simulated failure in ReserveSeat for {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": "Simulated seat reservation failure"
            })
        
        # Extract booking information
        flight_id = booking_data.get('flight_id')
        passengers_data = booking_data.get('passengers', [])
        
        if not flight_id or not passengers_data:
            return JsonResponse({
                "success": False,
                "error": "Missing flight_id or passengers data"
            })
        
        # Check if flight exists
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": f"Flight {flight_id} not found"
            })
        
        # Create reservation record
        reservation_data = {
            "flight_id": flight_id,
            "passengers": passengers_data,
            "status": "RESERVED",
            "seats_reserved": len(passengers_data)
        }
        
        saga_reservations[correlation_id] = reservation_data
        
        logger.info(f"[SAGA] Seat reserved successfully for {len(passengers_data)} passengers")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "reservation_id": correlation_id,
            "seats_reserved": len(passengers_data),
            "flight": {
                "id": flight.id,
                "flight_number": flight.flight_number,
                "origin": str(flight.origin),
                "destination": str(flight.destination)
            }
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ReserveSeat: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def confirm_booking(request):
    """SAGA Step 4: Confirm booking and create ticket"""
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
        
        # Create actual ticket using existing system
        flight = Flight.objects.get(id=reservation