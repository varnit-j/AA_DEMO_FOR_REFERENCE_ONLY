"""
Complete Enhanced SAGA Orchestrator with Robust Rollback
Fixes all memory queue persistence and compensation issues
"""
import logging
import uuid
import requests
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.utils import timezone
from .models import SagaTransaction, SagaPaymentAuthorization, SagaMilesAward, SeatReservation

logger = logging.getLogger(__name__)

class SagaStepDefinition:
    def __init__(self, name: str, action_url: str, compensation_url: str, timeout: int = 30):
        self.name = name
        self.action_url = action_url
        self.compensation_url = compensation_url
        self.timeout = timeout

class EnhancedBookingOrchestrator:
    def __init__(self):
        self.steps = [
            SagaStepDefinition("ReserveSeat", 
                             "http://localhost:8001/api/saga/reserve-seat/", 
                             "http://localhost:8001/api/saga/cancel-seat/",
                             timeout=30),
            SagaStepDefinition("AuthorizePayment", 
                             "http://localhost:8003/api/saga/authorize-payment/", 
                             "http://localhost:8003/api/saga/cancel-payment/",
                             timeout=45),
            SagaStepDefinition("AwardMiles", 
                             "http://localhost:8002/api/saga/award-miles/", 
                             "http://localhost:8002/api/saga/reverse-miles/",
                             timeout=30),
            SagaStepDefinition("ConfirmBooking", 
                             "http://localhost:8001/api/saga/confirm-booking/", 
                             "http://localhost:8001/api/saga/cancel-booking/",
                             timeout=60)
        ]
    
    def start_booking_saga(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced SAGA orchestrator with database persistence and proper rollback
        """
        correlation_id = booking_data.get('correlation_id', str(uuid.uuid4()))
        logger.info(f"[SAGA ENHANCED] Starting booking SAGA with correlation_id: {correlation_id}")
        
        # Create or get SAGA transaction record
        try:
            from .models import Flight
            flight = Flight.objects.get(id=booking_data.get('flight_id'))
            
            saga_transaction, created = SagaTransaction.objects.get_or_create(
                correlation_id=correlation_id,
                defaults={
                    'user_id': booking_data.get('user_id'),
                    'flight': flight,
                    'booking_data': booking_data,
                    'status': 'STARTED'
                }
            )
            
            if not created:
                logger.warning(f"[SAGA ENHANCED] SAGA transaction {correlation_id} already exists")
                
        except Exception as e:
            logger.error(f"[SAGA ENHANCED] Error creating SAGA transaction: {e}")
            return {
                "success": False,
                "correlation_id": correlation_id,
                "error": f"Failed to create SAGA transaction: {str(e)}"
            }
        
        completed_steps = []
        try:
            saga_transaction.status = 'IN_PROGRESS'
            saga_transaction.save()
            
            for i, step in enumerate(self.steps):
                logger.info(f"[SAGA ENHANCED] Executing step {i+1}/{len(self.steps)}: