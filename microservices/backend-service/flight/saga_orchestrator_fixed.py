"""
SAGA Orchestrator for Flight Booking - Fixed Implementation
"""
import logging
import uuid
import requests
from typing import Dict, Any
from .saga_log_storage import saga_log_storage
from .failed_booking_handler import create_failed_booking_record

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
                    "http://localhost:8002/api/saga/authorize-payment/",
                    "http://localhost:8002/api/saga/cancel-payment/"),
            SagaStep("AwardMiles",
                    "http://localhost:8003/api/saga/award-miles/",
                    "http://localhost:8003/api/saga/reverse-miles/"),
            SagaStep("ConfirmBooking", 
                    "http://localhost:8001/api/saga/confirm-booking/", 
                    "http://localhost:8001/api/saga/cancel-booking/")
        ]
    
    def start_booking_saga(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        correlation_id = str(uuid.uuid4())
        logger.info(f"[SAGA] Starting booking SAGA with correlation_id: {correlation_id}")
        
        # Add initial log entry
        saga_log_storage.add_log(
            correlation_id, "SAGA_START", "ORCHESTRATOR", "info",
            f"SAGA transaction initiated for flight {booking_data.get('flight_id')}"
        )
        
        logger.info(f"[PAYMENT_FLOW_DEBUG] ===== SAGA ORCHESTRATOR ENTRY =====")
        logger.info(f"[PAYMENT_FLOW_DEBUG] Received booking_data keys: {list(booking_data.keys())}")
        logger.info(f"[PAYMENT_FLOW_DEBUG] flight_id in booking_data: '{booking_data.get('flight_id')}'")
        logger.info(f"[PAYMENT_FLOW_DEBUG] user_id in booking_data: {booking_data.get('user_id')}")
        logger.info(f"[PAYMENT_FLOW_DEBUG] passengers count: {len(booking_data.get('passengers', []))}")
        
        completed_steps = []
        try:
            for i, step in enumerate(self.steps):
                logger.info(f"[SAGA] Executing step {i+1}/{len(self.steps)}: {step.name}")
                
                # Log step initiation
                saga_log_storage.add_log(
                    correlation_id, step.name, "ORCHESTRATOR", "info",
                    f"Step {i+1}: {step.name} initiated"
                )
                
                logger.info(f"[PAYMENT_FLOW_DEBUG] ===== SAGA STEP {i+1}: {step.name} =====")
                logger.info(f"[PAYMENT_FLOW_DEBUG] Step URL: {step.action_url}")
                
                step_data = {
                    "correlation_id": correlation_id,
                    "step_number": i + 1,
                    "booking_data": booking_data,
                    "simulate_failure": booking_data.get(f"simulate_{step.name.lower()}_fail", False)
                }
                
                logger.info(f"[PAYMENT_FLOW_DEBUG] Step data flight_id: '{step_data['booking_data'].get('flight_id')}'")
                logger.info(f"[PAYMENT_FLOW_DEBUG] Simulate failure: {step_data['simulate_failure']}")
                
                result = self._execute_step(step, step_data)
                
                if result.get("success"):
                    completed_steps.append(step)
                    logger.info(f"[SAGA] Step {step.name} completed successfully")
                    
                    # Log step success
                    saga_log_storage.add_log(
                        correlation_id, step.name, "ORCHESTRATOR", "success",
                        f"Step {step.name} completed successfully"
                    )
                else:
                    logger.error(f"[SAGA] Step {step.name} failed: {result.get('error', 'Unknown error')}")
                    
                    # Log step failure
                    saga_log_storage.add_log(
                        correlation_id, step.name, "ORCHESTRATOR", "error",
                        f"Step {step.name} failed: {result.get('error', 'Unknown error')}"
                    )
                    
                    compensation_result = self._execute_compensation(completed_steps, correlation_id, booking_data)
                    
                    # Create failed booking record for user to see in their bookings
                    error_message = f"SAGA failed at step {step.name}: {result.get('error', 'Unknown error')}"
                    logger.error(f"[SAGA ORCHESTRATOR] 🚨 SAGA FAILURE DETECTED - About to create failed booking record")
                    logger.error(f"[SAGA ORCHESTRATOR] 📊 User ID: {booking_data.get('user_id')}")
                    logger.error(f"[SAGA ORCHESTRATOR] 🎫 Flight ID: {booking_data.get('flight_id')}")
                    logger.error(f"[SAGA ORCHESTRATOR] ❌ Failed step: {step.name}")
                    logger.error(f"[SAGA ORCHESTRATOR] 💬 Error message: {error_message}")
                    
                    failed_ticket = create_failed_booking_record(
                        correlation_id=correlation_id,
                        booking_data=booking_data,
                        failed_step=step.name,
                        error_message=error_message,
                        compensation_result=compensation_result
                    )
                    
                    logger.info(f"[SAGA ORCHESTRATOR] 📝 Failed booking handler returned: {failed_ticket}")
                    if failed_ticket:
                        logger.info(f"[SAGA ORCHESTRATOR] ✅ Failed booking record created with ref: {failed_ticket.get('ref_no')}")
                    else:
                        logger.error(f"[SAGA ORCHESTRATOR] ❌ Failed booking handler returned None - no record created!")
                    
                    return {
                        "success": False,
                        "correlation_id": correlation_id,
                        "error": error_message,
                        "failed_step": step.name,
                        "compensation_result": compensation_result,
                        "failed_booking_ref": failed_ticket.get('ref_no') if failed_ticket else None
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
            
            # Create failed booking record for unexpected errors too
            error_message = f"SAGA execution error: {str(e)}"
            failed_ticket = create_failed_booking_record(
                correlation_id=correlation_id,
                booking_data=booking_data,
                failed_step="UNEXPECTED_ERROR",
                error_message=error_message,
                compensation_result=compensation_result
            )
            
            logger.info(f"[SAGA] Created failed booking record for exception: {failed_ticket.get('ref_no') if failed_ticket else 'None'}")
            
            return {
                "success": False,
                "correlation_id": correlation_id,
                "error": error_message,
                "compensation_result": compensation_result,
                "failed_booking_ref": failed_ticket.get('ref_no') if failed_ticket else None
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
        logger.info(f"[SAGA COMPENSATION] 🔄 Starting compensation for {len(completed_steps)} completed steps")
        logger.info(f"[SAGA COMPENSATION] 📋 Steps to compensate: {[step.name for step in completed_steps]}")
        
        # Log compensation initiation
        saga_log_storage.add_log(
            correlation_id, "COMPENSATION", "ORCHESTRATOR", "warning",
            f"Starting compensation for {len(completed_steps)} completed steps"
        )
        
        compensation_results = []
        for step in reversed(completed_steps):
            try:
                logger.info(f"[SAGA COMPENSATION] ⚡ Executing compensation for step: {step.name}")
                logger.info(f"[SAGA COMPENSATION] 🌐 Calling compensation URL: {step.compensation_url}")
                
                # DIAGNOSTIC: Add detailed logging for compensation debugging
                logger.info(f"[COMPENSATION_DEBUG] ===== COMPENSATION ATTEMPT =====")
                logger.info(f"[COMPENSATION_DEBUG] Step: {step.name}")
                logger.info(f"[COMPENSATION_DEBUG] URL: {step.compensation_url}")
                logger.info(f"[COMPENSATION_DEBUG] Correlation ID: {correlation_id}")
                logger.info(f"[COMPENSATION_DEBUG] Timeout: 30 seconds")
                
                compensation_data = {
                    "correlation_id": correlation_id,
                    "booking_data": booking_data,
                    "compensation_reason": f"SAGA failure - rolling back {step.name}"
                }
                
                logger.info(f"[COMPENSATION_DEBUG] Request payload: {compensation_data}")
                
                # Add connection test before actual request
                import time
                start_time = time.time()
                
                try:
                    response = requests.post(step.compensation_url, json=compensation_data, timeout=30)
                    end_time = time.time()
                    logger.info(f"[COMPENSATION_DEBUG] Request completed in {end_time - start_time:.2f} seconds")
                    logger.info(f"[COMPENSATION_DEBUG] Response status: {response.status_code}")
                    logger.info(f"[COMPENSATION_DEBUG] Response text: {response.text}")
                except requests.exceptions.RequestException as req_error:
                    logger.error(f"[COMPENSATION_DEBUG] Request failed: {req_error}")
                    raise req_error
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"[SAGA COMPENSATION] ✅ Compensation for {step.name} successful: {result.get('message', 'No message')}")
                    
                    # Log successful compensation
                    saga_log_storage.add_log(
                        correlation_id, f"COMPENSATE_{step.name}", "ORCHESTRATOR", "success",
                        f"Compensation for {step.name} completed successfully"
                    )
                    
                    compensation_results.append({
                        "step": step.name,
                        "success": True,
                        "result": result,
                        "timestamp": str(uuid.uuid4())[:8]  # Simple timestamp for demo
                    })
                else:
                    logger.error(f"[SAGA COMPENSATION] ❌ Compensation for {step.name} failed: HTTP {response.status_code}")
                    
                    # Log failed compensation
                    saga_log_storage.add_log(
                        correlation_id, f"COMPENSATE_{step.name}", "ORCHESTRATOR", "error",
                        f"Compensation for {step.name} failed: HTTP {response.status_code}"
                    )
                    
                    compensation_results.append({
                        "step": step.name,
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "timestamp": str(uuid.uuid4())[:8]
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