"""
SAGA Orchestrator for Flight Booking - Complete Implementation
Implements the SAGA pattern: ReserveSeat → AuthorizePayment → AwardMiles → ConfirmBooking
"""
import logging
import uuid
import requests
from typing import Dict, Any, Optional

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
    
    def start_booking_saga(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start the booking SAGA process"""
        correlation_id = str(uuid.uuid4())
        
        logger.info(f"[SAGA] Starting booking SAGA with correlation_id: {correlation_id}")
        
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
                else:
                    # Step failed, trigger compensation
                    logger.error(f"[SAGA] Step {step.name} failed: {result.get('error', 'Unknown error')}")
                    
                    # Execute compensation for completed steps
                    compensation_result = self._execute_compensation(completed_steps, correlation_id, booking_data)
                    
                    return {
                        "success": False,
                        "correlation_id": correlation_id,
                        "error": f"SAGA failed at step {step.name}: {result.get('error', 'Unknown error')}",
                        "failed_step": step.name,
                        "compensation_result": compensation_result
                    }
            
            # All steps completed successfully
            logger.info(f"[SAGA] All steps completed successfully for correlation_id: {correlation_id}")
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "message": "SAGA completed successfully