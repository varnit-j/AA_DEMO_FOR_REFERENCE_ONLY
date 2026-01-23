

"""
Complete SAGA Views for Backend Service - FIXED VERSION
Integrates SAGA pattern with existing booking system
"""
import logging
import json
import uuid
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Flight, Place, Week, SagaTransaction, SagaPaymentAuthorization, SagaMilesAward, SeatReservation, Ticket, Passenger
from .simple_views import stored_tickets
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# SAGA-specific storage
saga_reservations = {}
saga_orchestrator = None

# Initialize orchestrator
def get_orchestrator():
    global saga_orchestrator
    if saga_orchestrator is None:
        try:
            from .saga_orchestrator_fixed import BookingOrchestrator
            saga_orchestrator = BookingOrchestrator()
            logger.info("[SAGA] Orchestrator initialized successfully")
        except ImportError as e:
            logger.error(f"[SAGA] Failed to import orchestrator: {e}")
            saga_orchestrator = None
    return saga_orchestrator

@csrf_exempt
@require_http_methods(["POST"])
def start_booking_saga(request):
    """Start the complete SAGA booking process"""
    try:
        data = json.loads(request.body)
        logger.info(f"[SAGA] Starting booking SAGA with data: {data}")
        
        # Validate required fields
        flight_id = data.get('flight_id')
        passengers = data.get('passengers', [])
        contact_info = data.get('contact_info', {})
        
        if not flight_id or not passengers or not contact_info:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: flight_id, passengers, contact_info'
            }, status=400)
        
        # Get flight details
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Flight {flight_id} not found'
            }, status=404)
        
        # Prepare booking data for SAGA
        booking_data = {
            'flight_id': flight_id,
            'user_id': data.get('user_id', 1),
            'passengers': passengers,
            'contact_info': contact_info,
            'flight_fare': float(flight.economy_fare),
            'flight': {
                'id': flight.id,
                'flight_number': flight.flight_number,
                'economy_fare': float(flight.economy_fare),
                'origin': str(flight.origin),
                'destination': str(flight.destination)
            },
            # Failure simulation flags
            'simulate_reserveseat_fail': data.get('simulate_reserveseat_fail', False),
            'simulate_authorizepayment_fail': data.get('simulate_authorizepayment_fail', False),
            'simulate_awardmiles_fail': data.get('simulate_awardmiles_fail', False),
            'simulate_confirmbooking_fail': data.get('simulate_confirmbooking_fail', False)
        }
        
        # Get orchestrator and start SAGA
        orchestrator = get_orchestrator()
        if not orchestrator:
            return JsonResponse({
                'success': False,
                'error': 'SAGA orchestrator not available'
            }, status=500)
        
        # Create SAGA transaction record in database
        try:
            flight = Flight.objects.get(id=flight_id)
            saga_transaction = SagaTransaction.objects.create(
                correlation_id=str