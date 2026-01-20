
"""
SAGA Orchestrator for Flight Booking
Implements the SAGA pattern: ReserveSeat → AuthorizePayment → AwardMiles → ConfirmBooking
"""
import logging
import uuid
import requests
from typing import Dict, Any, Optional
from .saga_event_dispatcher import event_dispatcher, SagaEvent
from .models import Ticket

logger = logging.getLogger(__name__)

class SagaStep:
    """Represents a single step in the SAGA"""
    def __init__(self, name: str, action_url: str, compensation_url: str):
        self.name = name
        self.action_url = action_url
        self.compensation_url = compensation_url

class BookingOrchestrator:
    """SAGA Orchestrator for flight booking process"""
    
    def __init__(self):
        self.steps = [
            SagaStep("ReserveSeat", 
                    "http://localhost:8001/api/saga/reserve-seat/", 
                    "http://localhost:8001/api/saga/cancel-seat/"),
            SagaStep("AuthorizePayment", 
                    "http://localhost:8003/api/saga/authorize-payment/", 
                    "http://localhost:8003/api/saga/cancel-payment/"),
            SagaStep("AwardMiles", 
                    "http://localhost:8002/api/saga/award-miles/", 
                    "http://localhost:8002/api/saga/reverse-miles/"),
            SagaStep("ConfirmBooking", 
                    "http://localhost:8001/api/saga/confirm-booking/", 
                    "http://localhost:8001/api/saga/cancel-booking/")
        ]
        
        # Subscribe to compensation events
        event_dispatcher.subscribe("SAGA_STEP_FAILED", self._handle_step_failure)
        event_dispatcher.subscribe("SAGA_COMPENSATION_FAILED", self._handle_compensation_failure)
    
    def start_booking_saga(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start the booking SAGA process"""
        correlation_id = str(uuid.uuid4())
        
        logger.info(f"[SAGA] Starting booking SAGA with correlation_id: {correlation_id}")
        
        # Publish SAGA started event
        event_dispatcher.publish(SagaEvent(
            "SAGA_STARTED", 
            correlation_id, 
            {"booking_data": booking_data, "steps": [step.name for step in self.steps]}
        ))
        
        # Execute steps sequentially
        completed_steps = []
        try:
            for i, step in enumerate(self.steps):
                logger.info(f"[SAGA] Executing step {i+1}/{len(self.steps)}: {step.name}")
                
                # Prepare step data
                step_data = {
                    "correlation_id": correlation_id,
                    "step_number": i + 1,
                    "booking_data": booking_data,
                    "simulate_failure": booking_data.get(f"simulate_{step.name.lower()}_fail", False)
                }
                
                # Execute step
                result = self._execute_step(step, step_data)
                
                if result.get("success"):
                    completed_steps.append(step)
                    logger.info(f"[SAGA] Step {step.name} completed successfully")
                    
                    # Publish step completed event
                    event_dispatcher.publish(SagaEvent(
                        "SAGA_STEP_COMPLETED", 
                        correlation_id, 
                        {"step": step.name, "result": result}
                    ))
                else:
                    # Step failed, trigger compensation