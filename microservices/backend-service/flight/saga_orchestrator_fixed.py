"""
SAGA Orchestrator for Flight Booking - Fixed Implementation
"""
import logging
import uuid
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SagaStep:
    def __init__(self, name: str, action_url: str, compensation_url: str):
        self.name = name
        self.action_url = action_url
        self.compensation_url = compensation_url

class BookingOrchestrator:
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
        correlation_id = str(uuid.uuid4())
        logger.info(f"[SAGA] Starting booking SAGA with correlation_id: {correlation_id}")
        
        completed_steps = []
        try:
            for i, step in enumerate(self.steps):
                logger.info(f"[SAGA] Executing step {i+1}/{len(self.steps)}: {step.name}")
                
                step_data = {
                    "correlation_id": correlation_id,
                    "step_number": i + 1,
                    "booking_data": booking_data,
                    "simulate_failure": booking_data.get(f"simulate_{step.name.lower()}_fail", False)
                }
                
                result = self._execute_step(step, step_data)
                
                if result.get("success"):
                    completed_steps.append(step)
                    logger.info(f"[SAGA] Step {step.name} completed successfully")
                else:
                    logger.error(f"[SAGA] Step {step.name} failed: {result.get('error', 'Unknown error')}")
                    compensation_result = self._execute_compensation(completed_steps, correlation_id, booking_data)
                    
                    return {
                        "success": False,
                        "correlation_id": correlation_id,
                        "error": f"SAGA failed at step {step.name}: {result.get('error', 'Unknown error')}",
                        "failed_step": step.name,
                        "compensation_result": compensation_result
                    }
            
            logger.info(f"[SAGA] All steps completed successfully for correlation_id: {correlation_id}")
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "message": "SAGA completed successfully",
                "steps_completed": len(self.steps)
            }
            
        except Exception as e:
            logger.error(f"[SAGA] Unexpected error in SAGA execution: {e}")
            compensation_result = self._execute_compensation(completed_steps, correlation_id, booking_data)
            
            return {
                "success": False,
                "correlation_id": correlation_id,
                "error": f"SAGA execution error: {str(e)}",
                "compensation_result": compensation_result
            }
    
    def _execute_step(self, step: SagaStep, step_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"[SAGA] Calling {step.action_url}")
            response = requests.post(step.action_url, json=step_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"[SAGA] Step {step.name} response: {result}")
                return result
            else:
                logger.error(f"[SAGA] Step {step.name} HTTP error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"[SAGA] Step {step.name} error: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_compensation(self, completed_steps: list, correlation_id: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[SAGA] Starting compensation for {len(completed_steps)} completed steps")
        
        compensation_results = []
        for step in reversed(completed_steps):
            try:
                logger.info(f"[SAGA] Executing compensation for step: {step.name}")
                
                compensation_data = {
                    "correlation_id": correlation_id,
                    "booking_data": booking_data
                }
                
                response = requests.post(step.compensation_url, json=compensation_data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"[SAGA] Compensation for {step.name} successful")
                    compensation_results.append({
                        "step": step.name,
                        "success": True,
                        "result": result
                    })
                else:
                    logger.error(f"[SAGA] Compensation for {step.name} failed: HTTP {response.status_code}")
                    compensation_results.append({
                        "step": step.name,
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                logger.error(f"[SAGA] Compensation for {step.name} error: {e}")
                compensation_results.append({
                    "step": step.name,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total_compensations": len(compensation_results),
            "successful_compensations": len([r for r in compensation_results if r.get("success")]),
            "results": compensation_results
        }